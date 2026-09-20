"""Budgeted CD-PC enwik8 experiment. Self-contained Colab/CPU implementation.
Persistent paths are supplied by the caller; notebook uses mounted Google Drive.
"""
from __future__ import annotations
import contextlib, copy, dataclasses, hashlib, io, json, math, os, platform
import shutil, sys, tempfile, time, urllib.request, uuid, zipfile
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

VERSION = 'cdpc-enwik8-1.2'
EPS = 1/256
SPECS = [('base',0,0),('suffix',1,4),('suffix',2,4),('suffix',3,4),
         ('suffix',4,4),('suffix',6,4),('suffix',8,4),('suffix',3,16),
         ('suffix',6,16),('copy',1,2),('copy',2,2),('copy',3,2),('copy_suffix',3,2)]
NAMES = ['base' if a=='base' else f'{a}_{b}_{c}' for a,b,c in SPECS]
J = len(SPECS)
FIXED = [0,2,4,5,10]
ARMS = ['compressed_pc','compressed_bp','fixed_pc','fixed_bp','all_pc','all_bp','same_graph_noinfer']

@dataclass
class Config:
    seed: int = 104
    seeds: tuple = (7,19,37)
    width: int = 320
    layers: int = 6
    heads: int = 5
    context: int = 256
    burnin: int = 128
    memory: int = 16
    base_batch: int = 32
    base_hours: float = 3.25
    base_max_steps: int = 60000
    base_eval_every: int = 400
    base_checkpoint_seconds: int = 600
    dictionary_bytes: int = 16000000
    contexts_per_depth: int = 8192
    dictionary_min_support: int = 2
    fit_rows: int = 131072
    outcome_rows: int = 16384
    select_rows: int = 16384
    test_rows: int = 262144
    cache_blocks: int = 16
    cache_shard_blocks: int = 64
    gate_batch: int = 512
    gate_lr: float = .003
    weight_decay: float = .002
    strength: float = 2.
    beta: float = .05
    settle_steps: int = 24
    settle_lr: float = .3
    gate_initial: int = 256
    gate_trial: int = 64
    gate_final: int = 256
    gate_factor_max: int = 8
    gate_check_every: int = 128
    gate_checkpoint_seconds: int = 120
    final_reserve_seconds: int = 1800
    bootstrap_samples: int = 1000
    pilot: bool = False
    pilot_bytes: int = 500000
    pilot_base_steps: int = 32
    stop_after_base_step: int = 0  # Test hook; do not use in the main notebook.

    @classmethod
    def smoke(cls):
        return cls(width=32,layers=1,heads=2,context=64,burnin=32,memory=8,
                   base_batch=8,base_hours=.05,base_max_steps=24,base_eval_every=8,
                   dictionary_bytes=100000,contexts_per_depth=128,
                   fit_rows=1024,outcome_rows=256,select_rows=256,test_rows=1024,
                   cache_blocks=4,cache_shard_blocks=8,gate_batch=64,
                   gate_initial=8,gate_trial=2,gate_final=8,gate_factor_max=1,
                   gate_check_every=8,settle_steps=8,final_reserve_seconds=10,
                   bootstrap_samples=100,pilot=True,pilot_base_steps=24,seeds=(7,19))

    def validate(self):
        assert self.width % self.heads == 0
        assert self.burnin >= max(8,self.memory) and self.burnin < self.context
        assert self.context > 16 and len(self.seeds)>0
        n=self.context-self.burnin
        for r in [self.fit_rows,self.outcome_rows,self.select_rows,self.test_rows]: assert r % n == 0
        assert self.gate_factor_max>=1 and self.gate_trial>0


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for part in iter(lambda:f.read(8<<20),b''):h.update(part)
    return h.hexdigest()

def jsonbytes(obj): return (json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def cpu_tree(x):
    if isinstance(x,torch.Tensor):return x.detach().cpu().clone()
    if isinstance(x,dict):return {k:cpu_tree(v) for k,v in x.items()}
    if isinstance(x,list):return [cpu_tree(v) for v in x]
    if isinstance(x,tuple):return tuple(cpu_tree(v) for v in x)
    return copy.deepcopy(x)

def load_pt(path):return torch.load(path,map_location='cpu',weights_only=False)

class BudgetStop(RuntimeError):pass
class TestInterruption(RuntimeError):pass

class Store:
    """Write payload, verify its bytes, then write an immutable commit record.
    All prior versions are retained; incomplete/corrupt latest commits fall back.
    No background-only backup queue and no dependency on a local Colab disk.
    """
    def __init__(self,root,hours=7.5,work=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.work=Path(work or tempfile.mkdtemp(prefix='cdpc_work_'));self.work.mkdir(parents=True,exist_ok=True)
        self.started=time.monotonic();self.hours=hours;self.prior_seconds=0.;self.last_log=0
        p=self.root/'progress.jsonl'
        if p.exists():
            with open(p,errors='replace') as f:
                for line in f:
                    try:self.prior_seconds=max(self.prior_seconds,float(json.loads(line).get('elapsed_seconds',0)))
                    except (ValueError,TypeError):pass
        self.verified={}
    @property
    def elapsed(self):return self.prior_seconds+time.monotonic()-self.started
    @property
    def remaining(self):return self.hours*3600-self.elapsed
    def log(self,event,**kw):
        d=dict(event=event,elapsed_seconds=round(self.elapsed,3),remaining_minutes=round(self.remaining/60,1),**kw)
        line=json.dumps(d,allow_nan=False)
        print(line,flush=True)
        with open(self.root/'progress.jsonl','a') as f:f.write(line+'\n');f.flush();os.fsync(f.fileno())
    def guard(self,reserve=90):
        if self.remaining<reserve:raise BudgetStop(f'Runtime budget nearly exhausted; {self.remaining/60:.1f} minutes remain. Completed stages are retained.')
    def write(self,relative,data):
        path=self.root/relative;path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_name(path.name+'.partial-'+uuid.uuid4().hex)
        if isinstance(data,Path):
            expected=digest(data);shutil.copyfile(data,tmp)
        else:
            if isinstance(data,str):data=data.encode()
            expected=hashlib.sha256(data).hexdigest()
            with open(tmp,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        if digest(tmp)!=expected:raise IOError(f'Backup verification failed for {relative}')
        os.replace(tmp,path)
        if digest(path)!=expected:raise IOError(f'Published backup verification failed for {relative}')
        return path,expected
    def save(self,key,state):
        folder=self.root/'checkpoints'/key;folder.mkdir(parents=True,exist_ok=True)
        name=f'{time.time_ns():020d}-{uuid.uuid4().hex[:8]}'
        local=self.work/f'{uuid.uuid4().hex}.pt'
        try:
            torch.save(cpu_tree(state),local)
            path,sha=self.write(Path('checkpoints')/key/(name+'.pt'),local)
            meta=dict(file=path.name,sha256=sha,bytes=path.stat().st_size,elapsed_seconds=self.elapsed,version=VERSION)
            self.write(Path('checkpoints')/key/(name+'.json'),jsonbytes(meta))
        finally:
            if local.exists():local.unlink()
        self.log('checkpoint_saved',key=key,megabytes=round(meta['bytes']/1e6,2))
        return meta
    def load(self,key):
        folder=self.root/'checkpoints'/key
        if not folder.exists():return None
        manifests=sorted(folder.glob('*.json'),reverse=True)
        for m in manifests:
            try:
                meta=json.loads(m.read_text());p=folder/meta['file']
                if not p.exists() or p.stat().st_size!=meta['bytes'] or digest(p)!=meta['sha256']:raise IOError('checksum mismatch')
                return load_pt(p)
            except (OSError,ValueError,EOFError,RuntimeError,KeyError) as e:
                self.log('checkpoint_ignored',key=key,reason=type(e).__name__)
        if manifests:raise IOError(f'No valid checkpoint for {key}; restore its Drive files before resuming.')
        return None
    def lock_config(self,cfg):
        # A stop hook changes interruption timing only, not the experiment.
        spec=asdict(cfg);spec.pop('stop_after_base_step')
        src=Path(__file__).read_bytes();sig=hashlib.sha256(src).hexdigest()
        record=dict(version=VERSION,config=spec,source_sha256=sig)
        path=self.root/'experiment_config.json'
        if path.exists():
            old=json.loads(path.read_text())
            if old!=json.loads(jsonbytes(record)):raise ValueError('This run folder belongs to different code/configuration. Use the original notebook to resume, or a NEW RUN_NAME for a new experiment.')
        else:
            self.write('experiment_config.json',jsonbytes(record));self.write('code/cdpc_experiment.py',src)
            self.write('environment.json',jsonbytes(dict(python=sys.version,torch=torch.__version__,numpy=np.__version__,platform=platform.platform(),gpu=torch.cuda.get_device_name() if torch.cuda.is_available() else None)))


def obtain_data(store,cfg,local_source=None):
    p=store.root/'data/enwik8.bin';sha_path=store.root/'data/enwik8.sha256'
    if p.exists() and sha_path.exists():
        assert digest(p)==sha_path.read_text().strip(),'Corpus checksum mismatch'
        store.log('corpus_resumed',bytes=p.stat().st_size)
    else:
        if local_source is None:
            store.log('download_start',url='https://mattmahoney.net/dc/enwik8.zip')
            local=store.work/'enwik8.zip'
            with urllib.request.urlopen('https://mattmahoney.net/dc/enwik8.zip',timeout=60) as response,open(local,'wb') as f:
                while True:
                    block=response.read(1<<20)
                    if not block:break
                    f.write(block)
            with zipfile.ZipFile(local) as z:raw=z.read('enwik8')
            store.write('data/enwik8.zip',local)
        else:raw=Path(local_source).read_bytes()
        if len(raw)==100000000:
            assert hashlib.md5(raw).hexdigest()=='a1fa5ffddb56f4953e226637dabbb36a','Not the verified enwik8 file'
        elif not cfg.pilot:raise ValueError('The main experiment requires the complete verified enwik8 corpus.')
        if cfg.pilot:raw=raw[:cfg.pilot_bytes]
        p,sha=store.write('data/enwik8.bin',raw);store.write('data/enwik8.sha256',sha+'\n')
        store.log('corpus_saved',bytes=len(raw),sha256=sha)
    # Compute from a local copy; the verified durable original stays on Drive.
    local_raw=store.work/'enwik8.bin';shutil.copyfile(p,local_raw)
    assert digest(local_raw)==sha_path.read_text().strip(),'Local corpus copy failed verification'
    raw=np.memmap(local_raw,dtype=np.uint8,mode='r');n=len(raw);a=int(.9*n);v=int(.95*n)
    assert cfg.dictionary_bytes<a//2
    roles={'base_train':[0,a],'dictionary':[0,cfg.dictionary_bytes],
           'gate_train':[cfg.dictionary_bytes+cfg.context+1,a],
           'base_validation':[a,a+(v-a)//2],
           'gate_selection':[a+(v-a)//2,v], 'test':[v,n]}
    store.write('data/split_manifest.json',jsonbytes(dict(bytes=n,roles=roles,context=cfg.context,burnin=cfg.burnin,memory=cfg.memory,score_protocol='Nonoverlapping blocks; score latter half. This is not full-stream enwik8 benchmark bpb.')))
    return raw,roles

class Block(nn.Module):
    def __init__(self,d,heads):
        super().__init__();self.heads=heads;self.n1=nn.LayerNorm(d);self.qkv=nn.Linear(d,3*d);self.proj=nn.Linear(d,d)
        self.n2=nn.LayerNorm(d);self.ff=nn.Sequential(nn.Linear(d,4*d),nn.GELU(),nn.Linear(4*d,d))
    def forward(self,x):
        b,t,d=x.shape;q,k,v=self.qkv(self.n1(x)).reshape(b,t,3,self.heads,d//self.heads).permute(2,0,3,1,4).unbind(0)
        z=F.scaled_dot_product_attention(q,k,v,is_causal=True,dropout_p=0.).transpose(1,2).reshape(b,t,d)
        x=x+self.proj(z);return x+self.ff(self.n2(x))
class ByteTransformer(nn.Module):
    def __init__(self,cfg):
        super().__init__();self.cfg=cfg;self.emb=nn.Embedding(256,cfg.width);self.pos=nn.Embedding(cfg.context,cfg.width)
        self.blocks=nn.ModuleList([Block(cfg.width,cfg.heads) for _ in range(cfg.layers)]);self.norm=nn.LayerNorm(cfg.width)
        self.out=nn.Linear(cfg.width,256,bias=False);self.out.weight=self.emb.weight
        self.apply(self.init)
    @staticmethod
    def init(m):
        if isinstance(m,(nn.Linear,nn.Embedding)):
            nn.init.normal_(m.weight,std=.02)
            if isinstance(m,nn.Linear) and m.bias is not None:nn.init.zeros_(m.bias)
    def forward(self,x):
        h=self.emb(x)+self.pos(torch.arange(x.shape[1],device=x.device))
        for b in self.blocks:h=b(h)
        h=self.norm(h);return self.out(h),h

def autocast(device):
    if str(device).startswith('cuda'):return torch.autocast('cuda',dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16)
    return contextlib.nullcontext()

def raw_batch(raw,starts,context,device):
    a=np.stack([raw[int(s):int(s)+context+1] for s in starts]).astype(np.int64)
    t=torch.from_numpy(a).to(device);return t[:,:-1],t[:,1:]

def selected_starts(lo,hi,blocks,cfg,seed,spread=False):
    pool=np.arange(lo,hi-cfg.context,cfg.context+1,dtype=np.int64)
    if blocks>len(pool):raise ValueError(f'Not enough disjoint context blocks: {blocks} requested, {len(pool)} available')
    if spread:return pool[np.linspace(0,len(pool)-1,blocks,dtype=int)]
    return np.sort(np.random.default_rng(seed).choice(pool,blocks,replace=False))

@torch.no_grad()
def base_validation(model,raw,starts,cfg,device):
    model.eval();s=0.;n=0
    for lo in range(0,len(starts),cfg.base_batch):
        x,y=raw_batch(raw,starts[lo:lo+cfg.base_batch],cfg.context,device)
        with autocast(device):logits,_=model(x)
        l=F.cross_entropy(logits[:,cfg.burnin:].float().flatten(0,1),y[:,cfg.burnin:].flatten(),reduction='sum')
        s+=float(l);n+=y[:,cfg.burnin:].numel()
    return s/n/math.log(2)

def base_step(model,opt,scaler,raw,roles,cfg,step,plan,device):
    rng=np.random.default_rng(cfg.seed+step*1009)
    starts=rng.integers(roles['base_train'][0],roles['base_train'][1]-cfg.context-1,size=plan['batch'])
    x,y=raw_batch(raw,starts,cfg.context,device);model.train();opt.zero_grad(set_to_none=True)
    fraction=min(step/plan['steps'],1);warm=min(1.,(step+1)/max(20,min(500,plan['steps']//10)))
    lr=3e-4*warm*(.1+.9*.5*(1+math.cos(math.pi*fraction)))
    for g in opt.param_groups:g['lr']=lr
    with autocast(device):logits,_=model(x);loss=F.cross_entropy(logits.flatten(0,1),y.flatten())
    scaler.scale(loss).backward();scaler.unscale_(opt);nn.utils.clip_grad_norm_(model.parameters(),1.)
    scaler.step(opt);scaler.update();return float(loss.detach())/math.log(2)

def train_base(store,raw,roles,cfg,device):
    final=store.load('base_final')
    torch.manual_seed(cfg.seed);model=ByteTransformer(cfg).to(device)
    if final is not None:model.load_state_dict(final['model']);return model.eval(),final
    opt=torch.optim.AdamW(model.parameters(),lr=3e-4,weight_decay=.01)
    scaler=torch.amp.GradScaler('cuda',enabled=str(device).startswith('cuda') and not torch.cuda.is_bf16_supported())
    state=store.load('base_train')
    if state:
        model.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);scaler.load_state_dict(state['scaler'])
        start=state['step'];plan=state['plan'];best=state['best'];bestloss=state['bestloss'];beststep=state['beststep'];trace=state['trace'];active_seconds=state['active_seconds']
        store.log('base_resume',step=start,planned_steps=plan['steps'])
    else:
        plan={'steps':cfg.pilot_base_steps if cfg.pilot else cfg.base_max_steps,'batch':cfg.base_batch}
        # Benchmark separate fresh weights: no unrecorded warm-up updates enter the base.
        bench=copy.deepcopy(model);bo=torch.optim.AdamW(bench.parameters(),lr=3e-4);bs=torch.amp.GradScaler('cuda',enabled=scaler.is_enabled())
        while True:
            try:
                for k in range(3):base_step(bench,bo,bs,raw,roles,cfg,k,plan,device)
                if str(device).startswith('cuda'):torch.cuda.synchronize()
                tick=time.perf_counter()
                for k in range(3,11):base_step(bench,bo,bs,raw,roles,cfg,k,plan,device)
                if str(device).startswith('cuda'):torch.cuda.synchronize()
                rate=(time.perf_counter()-tick)/8;break
            except torch.cuda.OutOfMemoryError:
                bo.zero_grad(set_to_none=True);torch.cuda.empty_cache();plan['batch']//=2
                if plan['batch']<2:raise
        del bench,bo,bs
        if not cfg.pilot:plan['steps']=max(20,min(cfg.base_max_steps,int(cfg.base_hours*3600/(rate*1.20))))
        plan['benchmark_seconds_per_step']=rate
        best=cpu_tree(model.state_dict());bestloss=1e30;beststep=0;start=0;trace=[];active_seconds=0.
        store.log('base_plan',parameters=sum(p.numel() for p in model.parameters()),**plan)
    val_starts=selected_starts(*roles['base_validation'],8 if cfg.pilot else 128,cfg,cfg.seed+2,True)
    last_save=time.monotonic();segment=time.monotonic();last_log=0;step=start
    def save():
        nonlocal active_seconds,segment,last_save
        active_seconds+=time.monotonic()-segment;segment=time.monotonic()
        store.save('base_train',dict(model=model.state_dict(),optimizer=opt.state_dict(),scaler=scaler.state_dict(),step=step,plan=plan,best=best,bestloss=bestloss,beststep=beststep,trace=trace,active_seconds=active_seconds,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []))
        last_save=time.monotonic()
    if state is None:save()  # Durable initial state and schedule before training.
    try:
        for step0 in range(start,plan['steps']):
            store.guard(cfg.final_reserve_seconds+600 if not cfg.pilot else 5)
            if not cfg.pilot and active_seconds+time.monotonic()-segment>cfg.base_hours*3600:break
            loss=base_step(model,opt,scaler,raw,roles,cfg,step0,plan,device);step=step0+1
            if time.monotonic()-last_log>=30 or step==1:
                store.log('base_training',step=step,total=plan['steps'],train_bpb=round(loss,5),tokens_seen=step*plan['batch']*cfg.context);last_log=time.monotonic()
            if step%cfg.base_eval_every==0 or step==plan['steps']:
                v=base_validation(model,raw,val_starts,cfg,device);trace.append(dict(step=step,validation_bpb=v))
                if v<bestloss:bestloss=v;best=cpu_tree(model.state_dict());beststep=step
                store.log('base_validation',step=step,bpb=v,best_step=beststep)
            if time.monotonic()-last_save>=cfg.base_checkpoint_seconds:save()
            if cfg.stop_after_base_step and step==cfg.stop_after_base_step:save();raise TestInterruption('Requested base interruption')
    except BudgetStop:save();raise
    except KeyboardInterrupt:
        # An interrupt could land inside AdamW: keep the prior complete state.
        store.log('manual_stop',stage='base',recovery='Use the last fully committed checkpoint');raise
    v=base_validation(model,raw,val_starts,cfg,device)
    if v<bestloss:bestloss=v;best=cpu_tree(model.state_dict());beststep=step
    save();final=dict(model=best,step=beststep,trained_steps=step,validation_bpb=bestloss,plan=plan,trace=trace,parameters=sum(p.numel() for p in model.parameters()))
    store.save('base_final',final);model.load_state_dict(best);return model.eval(),final


def context_keys(x,k):
    """Exact unsigned packing, no hashing/collisions, up to eight bytes."""
    x=np.asarray(x,dtype=np.uint8);out=np.zeros(x.shape,dtype=np.uint64)
    for lag in range(k):
        if lag==0:out|=x.astype(np.uint64)
        else:out[...,lag:]|=x[...,:-lag].astype(np.uint64)<<np.uint64(8*lag)
    return out

class ReaderBank:
    def __init__(self,uni,tables):self.uni=uni;self.tables=tables
    @classmethod
    def fit(cls,raw,cfg,store):
        raw=np.asarray(raw[:cfg.dictionary_bytes]);uni=np.bincount(raw,minlength=256).astype(np.float64)+.1;uni=(uni/uni.sum()).astype(np.float32);tables={}
        for k in range(1,9):
            old=store.load(f'dictionary_depth_{k}')
            if old is not None:tables[k]=old;continue
            store.guard(cfg.final_reserve_seconds)
            tick=time.perf_counter();key=context_keys(raw[:-1],k)[k-1:];y=raw[k:]
            values,counts=np.unique(key,return_counts=True)
            keep=np.flatnonzero(counts>=cfg.dictionary_min_support)
            if len(keep)>cfg.contexts_per_depth:
                # Stable count/key ordering makes the retained dictionary deterministic.
                cut=np.partition(counts[keep],-cfg.contexts_per_depth)[-cfg.contexts_per_depth]
                high=keep[counts[keep]>cut];ties=keep[counts[keep]==cut]
                keep=np.r_[high,ties[:cfg.contexts_per_depth-len(high)]]
            keys=np.sort(values[keep]);matrix=np.zeros((len(keys),256),np.int32)
            if len(keys):
                for lo in range(0,len(key),1000000):
                    a=key[lo:lo+1000000];ids=np.searchsorted(keys,a);valid=ids<len(keys);valid &= keys[np.minimum(ids,len(keys)-1)]==a
                    np.add.at(matrix,(ids[valid],y[lo:lo+len(a)][valid]),1)
            tables[k]={'keys':keys,'counts':matrix,'totals':matrix.sum(1).astype(np.float32)}
            store.save(f'dictionary_depth_{k}',tables[k]);store.log('dictionary_depth',depth=k,contexts=len(keys),seconds=round(time.perf_counter()-tick,2))
        return cls(uni,tables)
    def probabilities(self,x,base):
        # x [blocks,T] is observed input. Row t predicts the NEXT byte x[t+1].
        x=np.asarray(x,dtype=np.uint8);b,t=x.shape;probs=np.empty((b,t,J,256),np.float32);support=np.zeros((b,t,J),np.float32)
        probs[:,:,0]=base;out={};sup={};ks={k:context_keys(x,k) for k in range(1,9)}
        for alpha in (4,16):
            p=np.broadcast_to(self.uni,(b,t,256)).copy();n=np.zeros((b,t),np.float32)
            for k in range(1,9):
                table=self.tables[k];keys=table['keys'];flat=ks[k].reshape(-1);ids=np.searchsorted(keys,flat)
                if len(keys):
                    valid=ids<len(keys);ids=np.minimum(ids,len(keys)-1);valid &= keys[ids]==flat
                    valid=valid.reshape(b,t);valid[:,:k-1]=False
                    c=table['counts'][ids].reshape(b,t,256).astype(np.float32);total=table['totals'][ids].reshape(b,t)
                    c=c*valid[...,None];total=total*valid
                    p=(alpha*p+c)/(alpha+total[...,None]);n=np.where(valid,total,n)
                out[k,alpha]=p.copy();sup[k,alpha]=n.copy()
        for j,(op,k,a) in enumerate(SPECS):
            if op=='suffix':probs[:,:,j]=(1-EPS)*out[k,a]+EPS/256;support[:,:,j]=sup[k,a]
        copy_counts={}
        earlier=np.tril(np.ones((t,t),bool),k=-1)
        for k in (1,2,3):
            key=ks[k];match=(key[:,:,None]==key[:,None,:]) & earlier
            match[:,:k-1,:]=False;match[:,:,:k-1]=False
            successors=np.eye(256,dtype=np.float32)[np.concatenate([x[:,1:],np.zeros((b,1),np.uint8)],1)]
            cc=match.astype(np.float32)@successors;copy_counts[k]=cc
        for j,(op,k,a) in enumerate(SPECS):
            if op.startswith('copy'):
                cc=copy_counts[k];n=cc.sum(-1);fallback=base if op=='copy' else (1-EPS)*out[6,4]+EPS/256
                probs[:,:,j]=(a*fallback+(1-EPS)*cc+EPS/256*n[...,None])/(a+n[...,None]);support[:,:,j]=n
        return probs,support


def extract_blocks(model,bank,raw,starts,cfg,device):
    x,y=raw_batch(raw,starts,cfg.context,device)
    with torch.no_grad(),autocast(device):logits,h=model(x)
    base=((1-EPS)*logits.float().softmax(-1)+EPS/256).cpu().numpy()
    xx=x.cpu().numpy().astype(np.uint8);yy=y.cpu().numpy()
    probs,support=bank.probabilities(xx,base)
    entropy=-(probs*np.log(probs)).sum(-1)/math.log(256);peak=probs.max(-1)
    arg=base.argmax(-1);agree=np.take_along_axis(probs,arg[:,:,None,None],axis=-1)[...,0]
    feat=np.concatenate([h.float().cpu().numpy(),np.stack([entropy,peak,np.log1p(support)/10,agree],-1).reshape(len(x),cfg.context,-1)],-1)
    qy=np.take_along_axis(probs,yy[:,:,None,None],axis=-1)[...,0]
    rows=np.arange(cfg.burnin,cfg.context);past=np.stack([qy[:,rows-lag,:] for lag in range(cfg.memory,0,-1)],2)
    # Current/future target likelihoods are not inputs to inference or features.
    positions=(np.asarray(starts)[:,None]+rows[None,:]+1).reshape(-1)
    return dict(features=feat[:,rows].reshape(-1,feat.shape[-1]).astype(np.float32),
                past=past.reshape(-1,cfg.memory,J).astype(np.float32),qy=qy[:,rows].reshape(-1,J).astype(np.float32),
                positions=positions,targets=yy[:,rows].reshape(-1).astype(np.uint8),
                blocks=np.repeat(np.asarray(starts),len(rows)))


def build_role_starts(raw,roles,cfg):
    n=cfg.context-cfg.burnin
    pool=selected_starts(*roles['gate_train'],(cfg.fit_rows+cfg.outcome_rows)//n,cfg,cfg.seed+20)
    # Shuffle block assignment, then sort within role; adjacent contexts never overlap.
    rng=np.random.default_rng(cfg.seed+21);pool=rng.permutation(pool);cut=cfg.fit_rows//n
    return {'fit':np.sort(pool[:cut]),'outcome':np.sort(pool[cut:]),
            'select':selected_starts(*roles['gate_selection'],cfg.select_rows//n,cfg,cfg.seed+22,True),
            'test':selected_starts(*roles['test'],cfg.test_rows//n,cfg,cfg.seed+23,True)}

def cache_role(store,role,starts,model,bank,raw,cfg,device):
    shards=[]
    for si,lo in enumerate(range(0,len(starts),cfg.cache_shard_blocks)):
        key=f'cache_{role}_{si:04d}';d=store.load(key)
        if d is None:
            store.guard(120 if role=='test' else cfg.final_reserve_seconds)
            tick=time.perf_counter();chunks=[];part=starts[lo:lo+cfg.cache_shard_blocks]
            for bi in range(0,len(part),cfg.cache_blocks):chunks.append(extract_blocks(model,bank,raw,part[bi:bi+cfg.cache_blocks],cfg,device))
            d={k:np.concatenate([c[k] for c in chunks],0) for k in chunks[0]}
            store.save(key,d);store.log('cache_progress',role=role,blocks_done=min(lo+len(part),len(starts)),blocks_total=len(starts),seconds=round(time.perf_counter()-tick,2))
        expected=np.repeat(starts[lo:lo+cfg.cache_shard_blocks],cfg.context-cfg.burnin)
        assert np.array_equal(d['blocks'],expected),'Cache/role mismatch'
        shards.append(d)
    return {k:np.concatenate([s[k] for s in shards],0) for k in shards[0]}


def tensor_data(data,device):
    return {k:torch.as_tensor(data[k],dtype=torch.float32,device=device) for k in ['features','past','qy']}
def normstats(data):return data['features'].mean(0),data['features'].std(0).clamp_min(.05)
class Gate(nn.Module):
    def __init__(self,mean,std,active,width,seed):
        super().__init__();g=torch.Generator(device='cpu').manual_seed(seed)
        self.register_buffer('mean',mean.clone());self.register_buffer('std',std.clone())
        self.weight=nn.Parameter((torch.randn(J,len(mean),generator=g)*.005).to(mean.device));self.bias=nn.Parameter(torch.zeros(J,device=mean.device))
        self.active=list(active);self.width=width
    def inputs(self,f):
        mask=torch.zeros_like(self.mean);mask[:self.width]=1
        for j in self.active:mask[self.width+4*j:self.width+4*j+4]=1
        return ((f-self.mean)/self.std).clamp(-8,8)*mask
    def prior(self,f):return F.linear(f,self.weight[self.active],self.bias[self.active])

def cegrad(z,q):
    w=z.softmax(-1);r=w*q;return w-r/r.sum(-1,keepdim=True).clamp_min(1e-20)
def memgrad(z,past):
    w=z.softmax(-1);r=w[:,None,:]*past;return w-(r/r.sum(-1,keepdim=True).clamp_min(1e-20)).mean(1)
def infer(u,past,cfg,strength=None,start=None,q=None,beta=0,steps=None):
    s=cfg.strength if strength is None else strength;z=u if start is None else start
    if s==0 and beta==0:return z
    for _ in range(cfg.settle_steps if steps is None else steps):
        grad=z-u
        if s:grad=grad+s*memgrad(z,past)
        if beta:grad=grad+beta*cegrad(z,q)
        z=z-cfg.settle_lr*grad
    return z

def gate_step(m,opt,data,ids,cfg,method,strength=None):
    a=m.active;x=m.inputs(data['features'][ids]);past=data['past'][ids][:,:,a];q=data['qy'][ids][:,a];opt.zero_grad(set_to_none=True)
    if method=='pc':
        with torch.no_grad():
            u=m.prior(x);free=infer(u,past,cfg,strength);ctl=infer(u,past,cfg,strength,start=free)
            nudged=infer(u,past,cfg,strength,start=free,q=q,beta=cfg.beta);delta=(ctl-nudged)/cfg.beta
            m.weight.grad=torch.zeros_like(m.weight);m.bias.grad=torch.zeros_like(m.bias)
            m.weight.grad[a]=delta.T@x/len(x);m.bias.grad[a]=delta.mean(0)
    else:
        u=m.prior(x);z=infer(u,past,cfg,strength);loss=-(z.softmax(-1)*q).sum(-1).clamp_min(1e-20).log().mean();loss.backward()
    nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step()

@torch.no_grad()
def gate_losses(m,data,cfg,strength=None,wrong=False,batch=2048):
    arr=[];a=m.active
    for lo in range(0,len(data['features']),batch):
        f=data['features'][lo:lo+batch];p=data['past'][lo:lo+batch][:,:,a]
        if wrong:p=p.roll(1,0)
        z=infer(m.prior(m.inputs(f)),p,cfg,strength);q=data['qy'][lo:lo+batch][:,a]
        arr.append(-(z.softmax(-1)*q).sum(-1).clamp_min(1e-20).log2())
    return torch.cat(arr)

def optimizer(m,cfg):return torch.optim.AdamW(m.parameters(),lr=cfg.gate_lr,weight_decay=cfg.weight_decay)
def make_gate(stats,active,cfg,seed,device):return Gate(*stats,active,cfg.width,seed).to(device)
def model_payload(m,opt):return dict(model=cpu_tree(m.state_dict()),optimizer=cpu_tree(opt.state_dict()),active=m.active.copy())
def restore_gate(payload,stats,cfg,seed,device):
    m=make_gate(stats,payload['active'],cfg,seed,device);m.load_state_dict(payload['model']);o=optimizer(m,cfg);o.load_state_dict(payload['optimizer']);return m,o


def fit_gate(store,key,m,opt,fit,select,cfg,steps,seed,method,strength=None):
    saved=store.load(key);tick=time.perf_counter();trace=[];start=0;training_seconds=0.
    if saved is not None:
        m.load_state_dict(saved['model']);opt.load_state_dict(saved['optimizer']);m.active=saved['active'];start=saved['step'];best=saved['best'];best_loss=saved['best_loss'];trace=saved['trace'];training_seconds=saved['training_seconds']
        if saved['done']:
            m.load_state_dict(best['model']);opt.load_state_dict(best['optimizer']);return saved
    else:
        best=model_payload(m,opt);best_loss=float(gate_losses(m,select,cfg,strength).mean());trace=[dict(step=0,bpb=best_loss)]
    last=time.monotonic();last_print=last;step=start
    # Same integer-index stream for a trial and its no-change control.
    def checkpoint(done=False):
        nonlocal tick,training_seconds,last
        training_seconds+=time.perf_counter()-tick;tick=time.perf_counter()
        out=dict(**model_payload(m,opt),step=step,steps=steps,best=best,best_loss=best_loss,trace=trace,training_seconds=training_seconds,done=done)
        store.save(key,out);last=time.monotonic();return out
    if saved is None:checkpoint()  # Also covers an interrupt in the first interval.
    try:
        for step0 in range(start,steps):
            store.guard(cfg.final_reserve_seconds)
            ids=np.random.default_rng(seed+step0*1009).integers(len(fit['features']),size=cfg.gate_batch)
            gate_step(m,opt,fit,torch.as_tensor(ids,device=fit['features'].device),cfg,method,strength);step=step0+1
            if step%cfg.gate_check_every==0 or step==steps:
                score=float(gate_losses(m,select,cfg,strength).mean());trace.append(dict(step=step,bpb=score))
                if score<best_loss:best_loss=score;best=model_payload(m,opt)
            if time.monotonic()-last_print>30:
                store.log('gate_training',key=key,step=step,total=steps,best_selection_bpb=best_loss);last_print=time.monotonic()
            if time.monotonic()-last>cfg.gate_checkpoint_seconds:checkpoint()
    except BudgetStop:checkpoint();raise
    except KeyboardInterrupt:
        store.log('manual_stop',stage=key,recovery='Use the last fully committed checkpoint');raise
    result=checkpoint(True);m.load_state_dict(best['model']);opt.load_state_dict(best['optimizer']);return result

@torch.no_grad()
def removal_screen(m,outcome,cfg):
    original=m.active.copy();scores=[]
    for j in original:
        if j==0:continue
        m.active=[k for k in original if k!=j]
        scores.append((float(gate_losses(m,outcome,cfg).mean()),j))
    m.active=original;return sorted(scores)


def choose_cap_plan(store,data,stats,cfg,device):
    saved=store.load('cap_plan')
    if saved:return saved
    times={};n=4 if cfg.pilot else 24
    for method in ['pc','bp']:
        m=make_gate(stats,list(range(J)),cfg,900,device);o=optimizer(m,cfg)
        ids=torch.arange(min(cfg.gate_batch,len(data['fit']['features'])),device=device)
        tick=time.perf_counter()
        for _ in range(n):gate_step(m,o,data['fit'],ids,cfg,method)
        if str(device).startswith('cuda'):torch.cuda.synchronize()
        times[method]=(time.perf_counter()-tick)/n
    m=make_gate(stats,list(range(J)),cfg,900,device)
    tick=time.perf_counter();gate_losses(m,data['select'],cfg);eval_seconds=time.perf_counter()-tick
    unit=cfg.gate_initial+8*(3*cfg.gate_trial)+cfg.gate_final
    # All arms use the same total optimizer update budget; include rejected trials.
    per_update=max(times.values())+eval_seconds/cfg.gate_check_every
    available=max(0,store.remaining-cfg.final_reserve_seconds-600)
    estimated=unit*len(ARMS)*len(cfg.seeds)*per_update*1.5
    factor=1 if cfg.pilot else max(1,min(cfg.gate_factor_max,int(available/max(estimated,1))))
    plan=dict(factor=factor,steps_per_arm=unit*factor,bench_seconds=times,selection_eval_seconds=eval_seconds,estimated_gate_hours=estimated*factor/3600,seeds=list(cfg.seeds),arms=ARMS,selection='Separate validation half; no test-based tuning',budget_matching='Optimizer updates including all candidate/control updates. FLOPs and seconds are reported separately.')
    store.save('cap_plan',plan);store.log('cap_plan',**plan);return plan


def run_arm(store,arm,seed,data,stats,cfg,plan,device):
    key=f'arm_{arm}_{seed}';done=store.load(key+'_final')
    if done:return done
    method='bp' if arm.endswith('bp') else 'pc';factor=plan['factor'];events=[];seconds=0.
    if arm=='same_graph_noinfer':
        prior=store.load(f'arm_compressed_pc_{seed}_final')
        if prior is None:raise RuntimeError('Same-graph control requires the preselected CD-PC graph')
        active=prior['active'];strength=0.
    else:active=list(range(J)) if arm.startswith(('compressed','all')) else FIXED;strength=None
    m=make_gate(stats,active,cfg,seed,device);opt=optimizer(m,cfg)
    if not arm.startswith('compressed'):
        info=fit_gate(store,key+'_fit',m,opt,data['fit'],data['select'],cfg,plan['steps_per_arm'],seed*100000,method,strength);seconds=info['training_seconds']
    else:
        info=fit_gate(store,key+'_initial',m,opt,data['fit'],data['select'],cfg,cfg.gate_initial*factor,seed*100000,method);seconds=info['training_seconds']
        for round_id in range(8):
            round_key=f'{key}_round_{round_id}';saved=store.load(round_key)
            if saved:
                m,opt=restore_gate(saved,stats,cfg,seed,device);events=saved['events'];seconds=saved['seconds'];continue
            screened=removal_screen(m,data['outcome'],cfg);candidate_ids=[v[1] for v in screened[:2]]
            origin=model_payload(m,opt);rs=seed*100000+(round_id+1)*1000
            control,co=restore_gate(origin,stats,cfg,seed,device)
            ci=fit_gate(store,round_key+'_control',control,co,data['fit'],data['select'],cfg,cfg.gate_trial*factor,rs,method);seconds+=ci['training_seconds']
            control_out=float(gate_losses(control,data['outcome'],cfg).mean());trials=[]
            for j in candidate_ids:
                tm,to=restore_gate(origin,stats,cfg,seed,device);tm.active.remove(j)
                ti=fit_gate(store,round_key+f'_drop_{j}',tm,to,data['fit'],data['select'],cfg,cfg.gate_trial*factor,rs,method);seconds+=ti['training_seconds']
                score=float(gate_losses(tm,data['select'],cfg).mean());outscore=float(gate_losses(tm,data['outcome'],cfg).mean())
                event=dict(round=round_id,removed=j,name=NAMES[j],screen_bpb=next(a for a,b in screened if b==j),selection_bpb=score,outcome_gain_vs_control=control_out-outscore,active_before=origin['active'])
                trials.append((score,j,model_payload(tm,to)));events.append(event)
            score,j,winner=min(trials,key=lambda x:(x[0],x[1]));m,opt=restore_gate(winner,stats,cfg,seed,device)
            store.save(round_key,dict(**model_payload(m,opt),events=events,seconds=seconds));store.log('cd_removal',arm=arm,seed=seed,round=round_id+1,removed=NAMES[j],active=len(m.active),selection_bpb=score)
        info=fit_gate(store,key+'_refit',m,opt,data['fit'],data['select'],cfg,cfg.gate_final*factor,seed*100000+90000,method);seconds+=info['training_seconds']
    final=dict(**model_payload(m,opt),arm=arm,seed=seed,steps=plan['steps_per_arm'],fit_search_seconds=seconds,selection_bpb=float(gate_losses(m,data['select'],cfg,strength).mean()),strength=cfg.strength if strength is None else strength,events=events)
    store.save(key+'_final',final);return final


def block_means(loss,data):
    _,inv=np.unique(data['blocks'],return_inverse=True);return np.bincount(inv,weights=loss)/np.bincount(inv)

def paired_bootstrap(delta,rng,n=1000):
    # Contiguous groups of 8 sampled context blocks, shared across seed contrasts.
    # Descriptive within-corpus interval; not independent dataset uncertainty.
    groups=np.array([np.mean(delta[k:k+8]) for k in range(0,len(delta),8)])
    vals=[]
    for _ in range(n):vals.append(float(groups[rng.integers(len(groups),size=len(groups))].mean()))
    return [float(x) for x in np.quantile(vals,[.025,.975])]


@torch.no_grad()
def fit_global_mixture(store,data):
    previous=store.load('global_mixture')
    if previous is not None:return previous
    q=data['fit']['qy'];w=q.new_full((J,),1/J)
    for step in range(200):
        r=q*w;r=r/r.sum(-1,keepdim=True);new=r.mean(0);new=new/new.sum()
        if float((new-w).abs().max())<1e-8:w=new;break
        w=new
    best_reader=int((-data['select']['qy'].log2().mean(0)).argmin())
    result=dict(weights=w.cpu(),iterations=step+1,best_reader=best_reader)
    store.save('global_mixture',result);return result


def evaluate(store,finals,test_np,stats,cfg,device,base_info,plan,stop_reason=None):
    test=tensor_data(test_np,device);rows=[];losses={}
    baseloss=-np.log2(test_np['qy'][:,0]);baseline=store.load('global_mixture');global_loss=-np.log2((test_np['qy']*baseline['weights'].numpy()).sum(1));single_loss=-np.log2(test_np['qy'][:,baseline['best_reader']]);rows.append(dict(arm='frozen_base',seed=None,bpb=float(baseloss.mean()),steps=0,readers=1,fit_search_seconds=0.))
    rows.append(dict(arm='global_reader_mixture',seed=None,bpb=float(global_loss.mean()),steps=baseline['iterations'],readers=J,fit_search_seconds=None))
    rows.append(dict(arm='validation_selected_reader',seed=None,bpb=float(single_loss.mean()),reader=NAMES[baseline['best_reader']],steps=0,readers=1,fit_search_seconds=None))
    for state in finals:
        name=f"{state['arm']}_{state['seed']}";saved=store.load('evaluation_'+name)
        if saved is None:
            m,_=restore_gate(state,stats,cfg,state['seed'],device)
            pred=gate_losses(m,test,cfg,state['strength']).cpu().numpy()
            noinf=gate_losses(m,test,cfg,0.).cpu().numpy()
            wrong=gate_losses(m,test,cfg,state['strength'],True).cpu().numpy()
            saved=dict(loss=pred,noinfer=noinf,wrong_prefix=wrong,blocks=test_np['blocks'],positions=test_np['positions'])
            store.save('evaluation_'+name,saved)
        pred=saved['loss'];losses[(state['arm'],state['seed'])]=block_means(pred,test_np)
        row=dict(arm=state['arm'],seed=state['seed'],bpb=float(pred.mean()),first_half_bpb=float(pred[:len(pred)//2].mean()),second_half_bpb=float(pred[len(pred)//2:].mean()),steps=state['steps'],readers=len(state['active']),fit_search_seconds=state['fit_search_seconds'],settling_gain=float((saved['noinfer']-pred).mean()),correct_prefix_gain=float((saved['wrong_prefix']-pred).mean()))
        rows.append(row);store.log('heldout_result',**row)
    aggregate=[]
    for arm in ARMS:
        rr=[r for r in rows if r['arm']==arm]
        if rr:aggregate.append(dict(arm=arm,seeds=len(rr),bpb=float(np.mean([r['bpb'] for r in rr])),first_half_bpb=float(np.mean([r['first_half_bpb'] for r in rr])),second_half_bpb=float(np.mean([r['second_half_bpb'] for r in rr])),readers=rr[0]['readers'],steps=rr[0]['steps'],mean_fit_search_seconds=float(np.mean([r['fit_search_seconds'] for r in rr]))))
    comparisons=[]
    for a,b in [('compressed_pc','fixed_pc'),('compressed_pc','compressed_bp'),('compressed_pc','all_pc'),('compressed_pc','same_graph_noinfer'),('fixed_pc','fixed_bp'),('all_pc','all_bp')]:
        seeds=[s for s in cfg.seeds if (a,s) in losses and (b,s) in losses]
        if not seeds:continue
        d=np.stack([losses[b,s]-losses[a,s] for s in seeds]);rng=np.random.default_rng(cfg.seed+80)
        comparisons.append(dict(method=a,comparator=b,gain_bpb=float(d.mean()),seed_gains=[float(x) for x in d.mean(1)],positive_seeds=int((d.mean(1)>0).sum()),seeds=len(seeds),block_interval=paired_bootstrap(d.mean(0),rng,cfg.bootstrap_samples)))
    report=dict(version=VERSION,budget_stop_reason=stop_reason,complete=len(finals)==len(ARMS)*len(cfg.seeds),pilot=cfg.pilot,base=base_info['parameters'],base_training_steps=base_info['trained_steps'],plan=plan,rows=rows,aggregate=aggregate,comparisons=comparisons,base_bpb=float(baseloss.mean()),global_mixture_bpb=float(global_loss.mean()),selected_reader_bpb=float(single_loss.mean()),selected_reader=NAMES[baseline['best_reader']],test_rows=len(baseloss),elapsed_hours=store.elapsed/3600,
                caveats=['One base pretraining seed, one corpus; cap seeds share the same base and dictionary.','CD has a fixed 13-reader grammar, not an unrestricted STLM/program-search engine.','BP also uses free-phase state inference; the no-inference arm is separately retrained on the PC-selected graph.','Equal optimizer updates do not equal FLOPs; five selected readers still share the dictionary.','Byte losses cover selected nonoverlapping contexts, not the full standard enwik8 test stream.','Intervals group eight scored blocks; they are descriptive, not cross-corpus or selection-corrected guarantees.'])
    store.write('results/summary.json',jsonbytes(report))
    lines=['# CD-PC enwik8 experiment','',f"Completed: {report['complete']}. Pilot: {cfg.pilot}.",f"Frozen-base bpb: {report['base_bpb']:.6f}; test targets: {len(baseloss):,}.",f"Global reader mixture: {report['global_mixture_bpb']:.6f}; validation-selected single reader ({report['selected_reader']}): {report['selected_reader_bpb']:.6f}.",'','| Arm | Seeds | bpb | Readers | Updates |','|---|---:|---:|---:|---:|']
    for r in aggregate:lines.append(f"| {r['arm']} | {r['seeds']} | {r['bpb']:.6f} | {r['readers']} | {r['steps']} |")
    lines+=['','Positive gain favors the first method.','','| Comparison | Gain (bpb) | Positive seeds | Descriptive block interval |','|---|---:|---:|---|']
    for r in comparisons:lines.append(f"| {r['method']} vs {r['comparator']} | {r['gain_bpb']:+.6f} | {r['positive_seeds']}/{r['seeds']} | {r['block_interval']} |")
    lines+=['','## Scope']+['- '+s for s in report['caveats']]
    store.write('results/REPORT.md','\n'.join(lines)+'\n')
    try:
        import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(10,5));ax.barh([r['arm'] for r in aggregate],[r['bpb'] for r in aggregate],color='#167d8d');ax.axvline(report['base_bpb'],color='#b74f39',linestyle='--',label='Frozen base');ax.set_xlabel('Bits per byte (lower is better)');ax.invert_yaxis();ax.legend();fig.tight_layout();tmp=store.work/'results.png';fig.savefig(tmp,dpi=160);plt.close(fig);store.write('results/comparison.png',tmp)
    except ImportError:pass
    # Compact return bundle; full state remains in Drive and is never deleted here.
    archive=store.work/'return_results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name in ['results/summary.json','results/REPORT.md','results/comparison.png','experiment_config.json','environment.json','data/split_manifest.json','data/shared_memory.json','progress.jsonl','code/cdpc_experiment.py']:
            p=store.root/name
            if p.exists():z.write(p,name)
        for state in finals:z.writestr(f"graphs/{state['arm']}_{state['seed']}.json",jsonbytes({k:state[k] for k in ['arm','seed','active','steps','selection_bpb','events']}))
    store.write('results/return_results.zip',archive)
    return report


def run(root,cfg=None,hours=7.5,local_source=None,allow_cpu=False):
    cfg=cfg or Config();cfg.validate()
    if not 0<hours<=8:raise ValueError('Choose a runtime budget above zero and at most 8 hours.')
    device='cuda' if torch.cuda.is_available() else 'cpu'
    if device=='cpu' and not (allow_cpu or cfg.pilot):raise RuntimeError('Choose a Colab GPU runtime before launching the full experiment.')
    torch.set_num_threads(2);torch.manual_seed(cfg.seed);np.random.seed(cfg.seed)
    if torch.cuda.is_available():torch.backends.cuda.matmul.allow_tf32=True
    store=Store(root,hours);store.lock_config(cfg);store.log('start',version=VERSION,device=device,resume=store.prior_seconds>0)
    try:
        raw,roles=obtain_data(store,cfg,local_source)
        model,base_info=train_base(store,raw,roles,cfg,device)
        bank=ReaderBank.fit(raw,cfg,store);starts=build_role_starts(raw,roles,cfg)
        store.write('data/role_block_starts.json',jsonbytes({k:v.tolist() for k,v in starts.items()}))
        data_np={role:cache_role(store,role,starts[role],model,bank,raw,cfg,device) for role in ['fit','outcome','select']}
        data={role:tensor_data(d,device) for role,d in data_np.items()};stats=normstats(data['fit'])
        fit_global_mixture(store,data)
        store.write('data/shared_memory.json',jsonbytes(dict(dictionary_training_bytes=cfg.dictionary_bytes,contexts=sum(len(t['keys']) for t in bank.tables.values()),count_table_bytes=sum(t['counts'].nbytes for t in bank.tables.values()),base_parameters=base_info['parameters'],gate_parameters=(cfg.width+4*J+1)*J,allocated_readers=J)))
        plan=choose_cap_plan(store,data,stats,cfg,device);finals=[]
        # Complete all fixed comparisons within a seed before starting the next.
        for seed in cfg.seeds:
            for arm in ARMS:finals.append(run_arm(store,arm,seed,data,stats,cfg,plan,device))
        store.save('evaluation_lock',dict(models=[dict(arm=s['arm'],seed=s['seed'],active=s['active'],selection_bpb=s['selection_bpb']) for s in finals],status='All final states chosen without test data'))
        test=cache_role(store,'test',starts['test'],model,bank,raw,cfg,device)
        report=evaluate(store,finals,test,stats,cfg,device,base_info,plan);store.log('complete',hours=round(store.elapsed/3600,3),results=str(store.root/'results/return_results.zip'));return report
    except (BudgetStop,KeyboardInterrupt) as e:
        store.log('paused',reason=str(e) or 'Manual interruption',resume='Rerun the same notebook with the same RUN_NAME. Completed stages and fitting checkpoints are reused.')
        store.write('results/STATUS.json',jsonbytes(dict(status='paused',reason=str(e),elapsed_hours=store.elapsed/3600)))
        # Use the reserved evaluation time to return honest partial comparisons.
        # Manual interrupts stop promptly instead. Future resumed fits keep the
        # already committed recipe and never inspect these held-out outcomes.
        if isinstance(e,BudgetStop) and locals().get('finals') and store.remaining>300:
            try:
                store.save('partial_evaluation_lock',dict(models=[dict(arm=s['arm'],seed=s['seed'],active=s['active']) for s in finals],reason=str(e)))
                test=cache_role(store,'test',starts['test'],model,bank,raw,cfg,device)
                report=evaluate(store,finals,test,stats,cfg,device,base_info,plan,stop_reason=str(e))
                store.log('partial_results_saved',completed_models=len(finals),requested_models=len(ARMS)*len(cfg.seeds))
                return report
            except (BudgetStop,KeyboardInterrupt):
                store.log('partial_evaluation_paused',reason='Insufficient remaining time or manual interruption')
        return {'complete':False,'paused':True,'reason':str(e),'run_root':str(store.root)}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--source');p.add_argument('--smoke',action='store_true');p.add_argument('--hours',type=float,default=7.5)
    args=p.parse_args();run(args.root,Config.smoke() if args.smoke else Config(),args.hours,args.source)
