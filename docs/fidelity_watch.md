# Fidelity watch (DEC-064a)

Every completed cell whose cap fidelity on the full validation split would have failed the formerly critical bounds
(mean KL > 0.001 nats or mean NLL increase > 0.01, either reference) is listed here with its numbers; the running
maximum per condition × dataset is kept so the lead can see whether it creeps. Entries are appended by the watch
(HT-8) after each cell; the orchestrator reports new entries at block boundaries and creep alerts immediately.
Labels are the DEC-064 secondary benchmark; nothing here vetoes a primary comparison.

| date | cell | dataset | condition | records | realization | KL (orig ‖ cap) | NLL Δ | ES95 | max | positions for 50 % KL | untouched | creep |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-09-18 | R1-64g mquake R1_learned_ff (chain S) | MQuAKE | R1_learned_ff (primary v5) | 300 | development | 0.00554 | +0.00560 | 0.114 | 8.19 | 171 (0.07 %) | 99.6 % | first entry; development reference |

Running maxima (KL): MQuAKE · R1_learned_ff 0.00554.

No-breach log: 2026-09-18 R1-64g mquake v0_stable (chain S, 300 records, development): zero observed loss / KL change on all 245,237 positions (radius-0 cap never fires on ordinary text) — no entry.

<!-- HT-8 managed watch: begin -->

## Automated verified watch (HT-8)

Manual notes above are preserved. This source-bound table is regenerated from the locked journal; one entry per recipe cell. Both references are shown. Near-zero target-token loss does not establish unchanged predictions or reader inactivity.

Audited cells: 49; breaching cells: 31; creep alerts: 5. Development and confirmatory observations remain labelled; benchmarks never veto primary comparisons.

| Cell identity / scope | Condition / dataset / realization / order | Actual records / checkpoint | Reference | Mean KL | NLL increase | ES95 loss | Max loss | Positions for half KL | Near-zero loss fraction | Creep |
|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` / development | R1_learned_ff / mquake / development_full_endpoints_R164f / seed64028 | 300 / 300 | capoff | 0.00554368762 | 0.00560097637 | 0.114467563 | 8.18755035 | 171 | 0.99631377 | none |
| `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` / development | R1_learned_ff / mquake / development_full_endpoints_R164f / seed64028 | 300 / 300 | original | 0.00554368762 | 0.00560097637 | 0.114467563 | 8.18755035 | 171 | 0.99631377 | none |
| `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` / development | R1_learned_ff / zsre / development_full_endpoints_R164f / seed64028 | 300 / 300 | capoff | 0.0022697245 | 0.00231001529 | 0.0474726905 | 9.94468865 | 64 | 0.99857689 | none |
| `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` / development | R1_learned_ff / zsre / development_full_endpoints_R164f / seed64028 | 300 / 300 | original | 0.0022697245 | 0.00231001529 | 0.0474726905 | 9.94468865 | 64 | 0.99857689 | none |
| `233ef059940a8a32881d4449ec1e0bc92135c3e075fedd50a378f3cb2f386d0a` / confirmatory | R1_learned_ff / zsre / 0 / 100 | 1000 / 1000 | capoff | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | new_running_maximum |
| `233ef059940a8a32881d4449ec1e0bc92135c3e075fedd50a378f3cb2f386d0a` / confirmatory | R1_learned_ff / zsre / 0 / 100 | 1000 / 1000 | original | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | new_running_maximum |
| `670dc28c3734f677d27585edbfe859362bcecff821b520439188de154ba4021b` / confirmatory | R1_learned_ff / zsre / 0 / 101 | 1000 / 1000 | capoff | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `670dc28c3734f677d27585edbfe859362bcecff821b520439188de154ba4021b` / confirmatory | R1_learned_ff / zsre / 0 / 101 | 1000 / 1000 | original | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `e2d852cb5df88203266bbade3286e8114f5afa55e16464e961626b34c1a9aa13` / confirmatory | R1_learned_ff / zsre / 0 / 102 | 1000 / 1000 | capoff | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `e2d852cb5df88203266bbade3286e8114f5afa55e16464e961626b34c1a9aa13` / confirmatory | R1_learned_ff / zsre / 0 / 102 | 1000 / 1000 | original | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `1238080b6993d46d6915b5686beb32ed4b69284d2e790b519b6fc7c2e511f49b` / confirmatory | R1_learned_ff / zsre / 0 / 103 | 1000 / 1000 | capoff | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `1238080b6993d46d6915b5686beb32ed4b69284d2e790b519b6fc7c2e511f49b` / confirmatory | R1_learned_ff / zsre / 0 / 103 | 1000 / 1000 | original | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `bc422f05f642d4f8fd9f0bcfe9eb406399648475c0fc113a20be62b113436f62` / confirmatory | R1_learned_ff / counterfact / 0 / 100 | 1000 / 1000 | capoff | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `bc422f05f642d4f8fd9f0bcfe9eb406399648475c0fc113a20be62b113436f62` / confirmatory | R1_learned_ff / counterfact / 0 / 100 | 1000 / 1000 | original | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `1e513a1440604fd9dff23e883ddea6a4d37efabc4e39b13f9a48f74f46752d2e` / confirmatory | R1_learned_ff / zsre / 0 / 104 | 1000 / 1000 | capoff | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `1e513a1440604fd9dff23e883ddea6a4d37efabc4e39b13f9a48f74f46752d2e` / confirmatory | R1_learned_ff / zsre / 0 / 104 | 1000 / 1000 | original | 0.00238149242 | 0.00245022572 | 0.0517612482 | 9.26226746 | 69 | 0.99805494 | none |
| `34e42454dc7c449a7d1248899a3d0c45b540229d575c6e49a6f490c4cc3566c6` / confirmatory | R1_learned_ff / counterfact / 0 / 101 | 1000 / 1000 | capoff | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `34e42454dc7c449a7d1248899a3d0c45b540229d575c6e49a6f490c4cc3566c6` / confirmatory | R1_learned_ff / counterfact / 0 / 101 | 1000 / 1000 | original | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `3757c0dc0feaff445e96a1032aa711833e617c31079f18aac296e14522dedde6` / confirmatory | R1_learned_ff / counterfact / 0 / 102 | 1000 / 1000 | capoff | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `3757c0dc0feaff445e96a1032aa711833e617c31079f18aac296e14522dedde6` / confirmatory | R1_learned_ff / counterfact / 0 / 102 | 1000 / 1000 | original | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `bae6aff38d749cf3d864f1348084ba6bf3ba270ad56d561628381bfae739026d` / confirmatory | R1_learned_ff / counterfact / 0 / 103 | 1000 / 1000 | capoff | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `bae6aff38d749cf3d864f1348084ba6bf3ba270ad56d561628381bfae739026d` / confirmatory | R1_learned_ff / counterfact / 0 / 103 | 1000 / 1000 | original | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `66300925ae4b4200b24fff0955ed5c057e002ee0982468a05bc867f5fd10adb3` / confirmatory | R1_learned_ff / counterfact / 0 / 104 | 1000 / 1000 | capoff | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `66300925ae4b4200b24fff0955ed5c057e002ee0982468a05bc867f5fd10adb3` / confirmatory | R1_learned_ff / counterfact / 0 / 104 | 1000 / 1000 | original | 0.00576537791 | 0.00584962582 | 0.122014002 | 15.3818045 | 119 | 0.99653804 | none |
| `e1bbec94233b2163317d228dcbf1b98cc1d4f672ea9d47d70f11ebbe6877de46` / confirmatory | R1_learned_ff / mquake / 0 / 100 | 300 / 300 | capoff | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | new_running_maximum |
| `e1bbec94233b2163317d228dcbf1b98cc1d4f672ea9d47d70f11ebbe6877de46` / confirmatory | R1_learned_ff / mquake / 0 / 100 | 300 / 300 | original | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | new_running_maximum |
| `0ce9de7e178e08aa4a0fdd81277abb96961860744c9e133194c98347e86d72cb` / confirmatory | R1_learned_ff / mquake / 0 / 101 | 300 / 300 | capoff | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `0ce9de7e178e08aa4a0fdd81277abb96961860744c9e133194c98347e86d72cb` / confirmatory | R1_learned_ff / mquake / 0 / 101 | 300 / 300 | original | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `1940590db6ae0be541bd4f531fcfa0e588815de63e97d2caf07db8e80690d8d1` / confirmatory | R1_learned_ff / mquake / 0 / 102 | 300 / 300 | capoff | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `1940590db6ae0be541bd4f531fcfa0e588815de63e97d2caf07db8e80690d8d1` / confirmatory | R1_learned_ff / mquake / 0 / 102 | 300 / 300 | original | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `f0fce47f17eac9fb96f2e01f081b30b51c05f3c93517ca277657aa2752f47b91` / confirmatory | R1_learned_ff / mquake / 0 / 103 | 300 / 300 | capoff | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `f0fce47f17eac9fb96f2e01f081b30b51c05f3c93517ca277657aa2752f47b91` / confirmatory | R1_learned_ff / mquake / 0 / 103 | 300 / 300 | original | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `d214aca63a8023e7a30f7570cc563d46243ca2103e414bececf8ee350106cd21` / confirmatory | R1_learned_ff / mquake / 0 / 104 | 300 / 300 | capoff | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `d214aca63a8023e7a30f7570cc563d46243ca2103e414bececf8ee350106cd21` / confirmatory | R1_learned_ff / mquake / 0 / 104 | 300 / 300 | original | 0.00712334183 | 0.00714615798 | 0.14612714 | 13.1442804 | 182 | 0.9958693 | none |
| `5fb7b789f235fe660f1fe219206a537c1e01d48f7491a9d9ca3db4a8d5694cb6` / confirmatory | R1_nonlearned / counterfact / 0 / 100 | 1000 / 1000 | capoff | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `5fb7b789f235fe660f1fe219206a537c1e01d48f7491a9d9ca3db4a8d5694cb6` / confirmatory | R1_nonlearned / counterfact / 0 / 100 | 1000 / 1000 | original | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `f893001ebfca1f3cc4c00a1783eca0ea39a99fdf2f2c564952274f80d28d41b9` / confirmatory | R1_nonlearned / counterfact / 0 / 101 | 1000 / 1000 | capoff | 0.0597805755 | 0.0595312224 | 1.20318962 | 20.2833748 | 1123 | 0.98080632 | new_running_maximum |
| `f893001ebfca1f3cc4c00a1783eca0ea39a99fdf2f2c564952274f80d28d41b9` / confirmatory | R1_nonlearned / counterfact / 0 / 101 | 1000 / 1000 | original | 0.0597805755 | 0.0595312224 | 1.20318962 | 20.2833748 | 1123 | 0.98080632 | new_running_maximum |
| `9d5f2ca8386cd2fa31e7dcd744de2f3e4aa5cb625973ac3c28d998fc19c39e6d` / confirmatory | R1_nonlearned / counterfact / 0 / 102 | 1000 / 1000 | capoff | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `9d5f2ca8386cd2fa31e7dcd744de2f3e4aa5cb625973ac3c28d998fc19c39e6d` / confirmatory | R1_nonlearned / counterfact / 0 / 102 | 1000 / 1000 | original | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `4af6d16ce3ca9d4539da256b5e86ae2d8b682feedf3a2c54cd5df6d5932f3789` / confirmatory | R1_nonlearned / counterfact / 0 / 103 | 1000 / 1000 | capoff | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `4af6d16ce3ca9d4539da256b5e86ae2d8b682feedf3a2c54cd5df6d5932f3789` / confirmatory | R1_nonlearned / counterfact / 0 / 103 | 1000 / 1000 | original | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `e9039ad97b5dc07993b6c996f04b8e3094ee8f65266481f1ed5229d6fe6a5d37` / confirmatory | R1_nonlearned / mquake / 0 / 100 | 300 / 300 | capoff | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `e9039ad97b5dc07993b6c996f04b8e3094ee8f65266481f1ed5229d6fe6a5d37` / confirmatory | R1_nonlearned / mquake / 0 / 100 | 300 / 300 | original | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `fe25c7fbb846c77410bf9cacd2843bcf2f47da950da3c02d9dce10d3d305f954` / confirmatory | R1_nonlearned / counterfact / 0 / 104 | 1000 / 1000 | capoff | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `fe25c7fbb846c77410bf9cacd2843bcf2f47da950da3c02d9dce10d3d305f954` / confirmatory | R1_nonlearned / counterfact / 0 / 104 | 1000 / 1000 | original | 0.0597793412 | 0.0595263036 | 1.20317591 | 20.2833748 | 1123 | 0.98080632 | none |
| `7c091ecbdbce85823e8abdf41e0906f8569c1417971e6bc6596d3f4b78003baa` / confirmatory | R1_nonlearned / mquake / 0 / 101 | 300 / 300 | capoff | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `7c091ecbdbce85823e8abdf41e0906f8569c1417971e6bc6596d3f4b78003baa` / confirmatory | R1_nonlearned / mquake / 0 / 101 | 300 / 300 | original | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `64f26bd674b7da0502286bbf588c28383a7f73eaaca44b1ac875156fa59065b0` / confirmatory | R1_nonlearned / mquake / 0 / 102 | 300 / 300 | capoff | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `64f26bd674b7da0502286bbf588c28383a7f73eaaca44b1ac875156fa59065b0` / confirmatory | R1_nonlearned / mquake / 0 / 102 | 300 / 300 | original | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `458638044e8baf00b0fdb41c994c53e0d5fd69054c8eabe57819f05dc4555237` / confirmatory | R1_nonlearned / mquake / 0 / 103 | 300 / 300 | capoff | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `458638044e8baf00b0fdb41c994c53e0d5fd69054c8eabe57819f05dc4555237` / confirmatory | R1_nonlearned / mquake / 0 / 103 | 300 / 300 | original | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `ed21300ae01a6223ce62f42b5b374577369c17211a3cd05434fa90be3e8bb3fd` / confirmatory | R1_nonlearned / mquake / 0 / 104 | 300 / 300 | capoff | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `ed21300ae01a6223ce62f42b5b374577369c17211a3cd05434fa90be3e8bb3fd` / confirmatory | R1_nonlearned / mquake / 0 / 104 | 300 / 300 | original | 0.0121762507 | 0.0120472241 | 0.243815181 | 15.0721631 | 262 | 0.99561241 | none |
| `13fc72b7ad0725721d24a35bd33fdd0cb8a612192b6e179e23aa4ef92cb4e0de` / confirmatory | v0_stable / zsre / 0 / 100 | unavailable / 1000 | capoff | 0.00116430329 | 0.000860380696 | 0.0213013776 | 25.8592601 | 13 | 0.99868291 | new_running_maximum |
| `13fc72b7ad0725721d24a35bd33fdd0cb8a612192b6e179e23aa4ef92cb4e0de` / confirmatory | v0_stable / zsre / 0 / 100 | unavailable / 1000 | original | 0.00116430329 | 0.000860380696 | 0.0213013776 | 25.8592601 | 13 | 0.99868291 | new_running_maximum |
| `1567dd5e5134d3c3bfabe3c800c867950a8b9cfaf1c221af51da540e17bcaf79` / confirmatory | v0_stable / zsre / 0 / 101 | unavailable / 1000 | capoff | 0.00185172225 | 0.00155231076 | 0.0379701374 | 27.6841654 | 19 | 0.99720271 | above_twice_development_reference, new_running_maximum |
| `1567dd5e5134d3c3bfabe3c800c867950a8b9cfaf1c221af51da540e17bcaf79` / confirmatory | v0_stable / zsre / 0 / 101 | unavailable / 1000 | original | 0.00185172225 | 0.00155231076 | 0.0379701374 | 27.6841654 | 19 | 0.99720271 | above_twice_development_reference, new_running_maximum |
| `685514501811adc9afc20d226ff93abfd11726f859fe4d753b48bd3602dab50d` / confirmatory | v0_stable / zsre / 0 / 103 | unavailable / 1000 | capoff | 0.00145363992 | 0.00120613705 | 0.0288660776 | 27.6841654 | 13 | 0.99829553 | none |
| `685514501811adc9afc20d226ff93abfd11726f859fe4d753b48bd3602dab50d` / confirmatory | v0_stable / zsre / 0 / 103 | unavailable / 1000 | original | 0.00145363992 | 0.00120613705 | 0.0288660776 | 27.6841654 | 13 | 0.99829553 | none |
| `947c0ba01d50c65eef575f552e86683faec1adbfee18d0215513ee1e881587a4` / confirmatory | v0_stable / zsre / 0 / 104 | unavailable / 1000 | capoff | 0.00153617076 | 0.00116742865 | 0.0272186768 | 27.6841654 | 11 | 0.99865029 | none |
| `947c0ba01d50c65eef575f552e86683faec1adbfee18d0215513ee1e881587a4` / confirmatory | v0_stable / zsre / 0 / 104 | unavailable / 1000 | original | 0.00153617076 | 0.00116742865 | 0.0272186768 | 27.6841654 | 11 | 0.99865029 | none |

### Running maxima (all audited cells, including no-breach cells)

| Condition : dataset | Reference | Maximum KL | Maximum signed NLL increase | Development reference cell |
|---|---|---:|---:|---|
| R1_learned_ff:counterfact | capoff | 0.00576537791 | 0.00584962582 | `unavailable` |
| R1_learned_ff:counterfact | original | 0.00576537791 | 0.00584962582 | `unavailable` |
| R1_learned_ff:mquake | capoff | 0.00712334183 | 0.00714615798 | `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` |
| R1_learned_ff:mquake | original | 0.00712334183 | 0.00714615798 | `e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4` |
| R1_learned_ff:zsre | capoff | 0.00238149242 | 0.00245022572 | `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` |
| R1_learned_ff:zsre | original | 0.00238149242 | 0.00245022572 | `b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1` |
| R1_nonlearned:counterfact | capoff | 0.0597805755 | 0.0595312224 | `unavailable` |
| R1_nonlearned:counterfact | original | 0.0597805755 | 0.0595312224 | `unavailable` |
| R1_nonlearned:mquake | capoff | 0.0121762507 | 0.0120472241 | `unavailable` |
| R1_nonlearned:mquake | original | 0.0121762507 | 0.0120472241 | `unavailable` |
| R1_nonlearned:zsre | capoff | 0.000314584493 | 0.000316561304 | `unavailable` |
| R1_nonlearned:zsre | original | 0.000314584493 | 0.000316561304 | `unavailable` |
| v0_stable:counterfact | capoff | 0 | 0 | `unavailable` |
| v0_stable:counterfact | original | 0 | 0 | `unavailable` |
| v0_stable:mquake | capoff | 0 | 0 | `29efe01659d59eafa4daf6c07dbbd45ba7ef97f1aee549ca95763aa0df8eba61` |
| v0_stable:mquake | original | 0 | 0 | `29efe01659d59eafa4daf6c07dbbd45ba7ef97f1aee549ca95763aa0df8eba61` |
| v0_stable:zsre | capoff | 0.00185172225 | 0.00155231076 | `d9cbf00f433af01b870b7e6a880e41c74689ecef4ac9e8ebcf90be639735fd77` |
| v0_stable:zsre | original | 0.00185172225 | 0.00155231076 | `d9cbf00f433af01b870b7e6a880e41c74689ecef4ac9e8ebcf90be639735fd77` |

### Creep alerts — orchestrator delivery queue

- **CREEP** `233ef059940a8a32881d4449ec1e0bc92135c3e075fedd50a378f3cb2f386d0a` (R1_learned_ff:zsre): capoff mean_kl 0.00238149242 > 0.0022697245 (new_running_maximum); capoff mean_signed_nll_increase 0.00245022572 > 0.00231001529 (new_running_maximum); original mean_kl 0.00238149242 > 0.0022697245 (new_running_maximum); original mean_signed_nll_increase 0.00245022572 > 0.00231001529 (new_running_maximum). Orchestrator reports immediately; this is not an admission veto.
- **CREEP** `e1bbec94233b2163317d228dcbf1b98cc1d4f672ea9d47d70f11ebbe6877de46` (R1_learned_ff:mquake): capoff mean_kl 0.00712334183 > 0.00554368762 (new_running_maximum); capoff mean_signed_nll_increase 0.00714615798 > 0.00560097637 (new_running_maximum); original mean_kl 0.00712334183 > 0.00554368762 (new_running_maximum); original mean_signed_nll_increase 0.00714615798 > 0.00560097637 (new_running_maximum). Orchestrator reports immediately; this is not an admission veto.
- **CREEP** `f893001ebfca1f3cc4c00a1783eca0ea39a99fdf2f2c564952274f80d28d41b9` (R1_nonlearned:counterfact): capoff mean_kl 0.0597805755 > 0.0597793412 (new_running_maximum); capoff mean_signed_nll_increase 0.0595312224 > 0.0595263036 (new_running_maximum); original mean_kl 0.0597805755 > 0.0597793412 (new_running_maximum); original mean_signed_nll_increase 0.0595312224 > 0.0595263036 (new_running_maximum). Orchestrator reports immediately; this is not an admission veto.
- **CREEP** `13fc72b7ad0725721d24a35bd33fdd0cb8a612192b6e179e23aa4ef92cb4e0de` (v0_stable:zsre): capoff mean_kl 0.00116430329 > 0.000788590677 (new_running_maximum); capoff mean_signed_nll_increase 0.000860380696 > 0.000855162037 (new_running_maximum); original mean_kl 0.00116430329 > 0.000788590677 (new_running_maximum); original mean_signed_nll_increase 0.000860380696 > 0.000855162037 (new_running_maximum). Orchestrator reports immediately; this is not an admission veto.
- **CREEP** `1567dd5e5134d3c3bfabe3c800c867950a8b9cfaf1c221af51da540e17bcaf79` (v0_stable:zsre): capoff mean_kl 0.00185172225 > 0.00116430329 (new_running_maximum); capoff mean_kl 0.00185172225 > 0.00157718135 (above_twice_development_reference); capoff mean_signed_nll_increase 0.00155231076 > 0.000860380696 (new_running_maximum); original mean_kl 0.00185172225 > 0.00116430329 (new_running_maximum); original mean_kl 0.00185172225 > 0.00157718135 (above_twice_development_reference); original mean_signed_nll_increase 0.00155231076 > 0.000860380696 (new_running_maximum). Orchestrator reports immediately; this is not an admission veto.

<!-- HT-8 managed watch: end -->
Creep alert 2026-09-18 18:42 EDT (confirmatory, cell 233ef059…, primary v5 zsRE r0 order 100, 1,000 records): mean KL 0.002381 / NLL Δ 0.002450 (both references) vs the development reference 0.002270 / 0.002310 (300 records) — new running maximum for zsRE · R1_learned_ff; relayed to the lead (lead queue item 101).

