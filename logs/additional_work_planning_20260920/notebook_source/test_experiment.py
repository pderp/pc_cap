"""Meaningful causality, numerical, checkpoint and data-role checks."""
import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
import torch
from cdpc_experiment import *

class Checks(unittest.TestCase):
    def setUp(self):torch.set_num_threads(2)
    def cfg(self):return Config.smoke()
    def bank(self,root):
        c=self.cfg();c.dictionary_bytes=1600;c.contexts_per_depth=128
        raw=np.frombuffer((b'abcXabcY hello hello !\x00\xff '*100),np.uint8)
        return ReaderBank.fit(raw,c,Store(root,1)),raw,c
    def test_vector_readers_match_scalar_and_are_normalized(self):
        with tempfile.TemporaryDirectory() as td:
            bank,raw,c=self.bank(td);x=np.array([raw[200:264],raw[500:564]])
            base=np.broadcast_to(np.ones(256)/256,(2,64,256)).astype(np.float32)
            q,s=bank.probabilities(x,base)
            np.testing.assert_allclose(q.sum(-1),1,atol=4e-7);self.assertGreaterEqual(q.min(),EPS/256-1e-8)
            for b,t in [(0,20),(1,60)]:
                prefix=bytes(x[b,:t+1]);preds={}
                for a in [4,16]:
                    p=bank.uni.astype(np.float64).copy()
                    for k in range(1,9):
                        key=int.from_bytes(prefix[-k:],'big');tab=bank.tables[k];where=np.flatnonzero(tab['keys']==key)
                        if len(where):p=(a*p+tab['counts'][where[0]])/(a+tab['totals'][where[0]])
                        preds[k,a]=p.copy()
                for j,(op,k,a) in enumerate(SPECS):
                    if op=='base':expected=base[b,t]
                    elif op=='suffix':expected=(1-EPS)*preds[k,a]+EPS/256
                    else:
                        count=np.zeros(256)
                        for j0 in range(k,len(prefix)):
                            if prefix[j0-k:j0]==prefix[-k:]:count[prefix[j0]]+=1
                        fallback=base[b,t] if op=='copy' else (1-EPS)*preds[6,4]+EPS/256
                        expected=(a*fallback+(1-EPS)*count+EPS/256*count.sum())/(a+count.sum())
                    np.testing.assert_allclose(q[b,t,j],expected,atol=4e-7,rtol=1e-5)
    def test_target_future_edits_cannot_change_prediction_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            bank,raw,c=self.bank(td);torch.manual_seed(2);model=ByteTransformer(c).eval()
            a=extract_blocks(model,bank,raw,np.array([400]),c,'cpu')
            changed=raw.copy();target=400+c.burnin+1;changed[target:]=255
            b=extract_blocks(model,bank,changed,np.array([400]),c,'cpu')
            for k in ['features','past']:np.testing.assert_allclose(a[k][0],b[k][0],atol=0,rtol=0)
            self.assertNotEqual(int(a['targets'][0]),int(b['targets'][0]))
            d=tensor_data(a,'cpu');e=tensor_data(b,'cpu');m=make_gate(normstats(d),list(range(J)),c,3,'cpu')
            def state(x):return infer(m.prior(m.inputs(x['features'][:1])),x['past'][:1],c)
            torch.testing.assert_close(state(d),state(e),atol=0,rtol=0)
    def test_energy_gradient_and_equilibrium_credit(self):
        torch.manual_seed(2);c=self.cfg();c.strength=.7;c.settle_steps=160;c.beta=1e-5
        u=torch.randn(7,4,dtype=torch.float64)*.3;p=torch.rand(7,8,4,dtype=torch.float64)+.02;q=torch.rand(7,4,dtype=torch.float64)+.02
        z=u.clone().requires_grad_();w=z.softmax(-1)
        energy=.5*(z-u).square().sum()-c.strength*(w[:,None,:]*p).sum(-1).log().mean(1).sum()-c.beta*(w*q).sum(-1).log().sum()
        expected=z-u+c.strength*memgrad(z,p)+c.beta*cegrad(z,q)
        grad=torch.autograd.grad(energy,z)[0];torch.testing.assert_close(grad,expected,atol=1e-12,rtol=1e-10)
        prior=u.clone().requires_grad_();free=infer(prior,p,c);obj=-(free.softmax(-1)*q).sum(-1).log().sum();bp=torch.autograd.grad(obj,prior)[0]
        with torch.no_grad():
            f=infer(u,p,c);control=infer(u,p,c,start=f);nudged=infer(u,p,c,start=f,q=q,beta=c.beta)
        self.assertLess(float(((control-nudged)/c.beta-bp).norm()/bp.norm()),1e-4)
    def test_verified_checkpoint_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            st=Store(td,1);st.save('model',{'value':1});st.save('model',{'value':2})
            self.assertEqual(st.load('model')['value'],2)
            last=sorted((Path(td)/'checkpoints/model').glob('*.json'))[-1];meta=json.loads(last.read_text());(last.parent/meta['file']).write_bytes(b'broken')
            self.assertEqual(st.load('model')['value'],1)
    def test_gate_resume_is_bitwise_and_optimizer_continues(self):
        c=self.cfg();c.gate_check_every=4;torch.manual_seed(123)
        d={'features':torch.randn(80,c.width+4*J),'past':torch.rand(80,c.memory,J)+.001,'qy':torch.rand(80,J)+.001};stats=normstats(d)
        with tempfile.TemporaryDirectory() as td:
            for method in ['pc','bp']:
                s=Store(Path(td)/method,1);m=make_gate(stats,FIXED,c,7,'cpu');o=optimizer(m,c)
                full=fit_gate(s,'whole',m,o,d,d,c,12,77,method)
                m2=make_gate(stats,FIXED,c,7,'cpu');o2=optimizer(m2,c)
                part=fit_gate(s,'part',m2,o2,d,d,c,4,77,method);part['done']=False;part['steps']=12;s.save('part',part)
                resumed=fit_gate(s,'part',m2,o2,d,d,c,12,77,method)
                for k in full['model']:torch.testing.assert_close(full['model'][k],resumed['model'][k],atol=0,rtol=0)
                torch.testing.assert_close(gate_losses(m,d,c),gate_losses(m2,d,c),atol=0,rtol=0)
                for k in full['optimizer']['state']:
                    for field in ['step','exp_avg','exp_avg_sq']:torch.testing.assert_close(full['optimizer']['state'][k][field],resumed['optimizer']['state'][k][field],atol=0,rtol=0)
    def test_base_resume_is_bitwise(self):
        c=self.cfg();c.pilot_base_steps=8;c.base_max_steps=8;c.base_eval_every=4
        raw=np.frombuffer(b'The captain is Mira. The cook is Leo. '*15000,np.uint8);roles={'base_train':[0,400000],'base_validation':[400000,420000]}
        with tempfile.TemporaryDirectory() as td:
            whole=Store(Path(td)/'whole',1);a,af=train_base(whole,raw,roles,c,'cpu')
            resume=Store(Path(td)/'resume',1);c2=copy.copy(c);c2.stop_after_base_step=4
            with self.assertRaises(TestInterruption):train_base(resume,raw,roles,c2,'cpu')
            b,bf=train_base(resume,raw,roles,c,'cpu')
            for k in af['model']:torch.testing.assert_close(af['model'][k],bf['model'][k],atol=0,rtol=0)
    def test_nonoverlapping_split_roles(self):
        c=self.cfg();n=500000;roles={'gate_train':[100065,450000],'gate_selection':[462500,475000],'test':[475000,n]}
        s=build_role_starts(None,roles,c)
        groups=[]
        for role,v in s.items():
            spans=set()
            for start in v:spans.update(range(int(start),int(start)+c.context+1))
            for other in groups:self.assertFalse(spans & other)
            groups.append(spans)

if __name__=='__main__':unittest.main(verbosity=2)
