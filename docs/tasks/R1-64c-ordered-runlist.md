# R1-64c ordered owner profiling run list

CPU inspections completed; none of these experiments was launched by this lane. Owner must hold the GPU lease, enforce MemAvailable and record failures/elapsed wall time. Run sequentially after chain H. These are development recipes; MQuAKE awaits R1-73.

| Order | Dataset | Condition | Profile | Recipe SHA-256 | Reader / continued checkpoint SHA-256 |
|---:|---|---|---|---|---|
| 1 | zsre | R1_nonlearned | incremental | 88e1057ab589948eaf51fd46292276ef5b8ed6ecb8ad03e31917f424878ace32 | a0e50ef72af48963062f8acabcf02ca66171d5d87f12cebf7074978a38a8317c |
| 2 | zsre | v0_stable | full | ca13fe8b335228873edeb05548d027e88e3c2d7e0f42039592d6165f1cccbb91 | Original frozen base; no learned reader/continued checkpoint |
| 3 | zsre | matched_update | full | 6fe37dc6aa241962a86218dcfb5518f9a180e39a7a4d4a14d7fe4dbe1b4d8f00 | Original frozen base; no learned reader/continued checkpoint |
| 4 | zsre | v0_live_C1 | full | b3773723158c1ea149ca2c0816d7ca95b9cf93f6f3529a326ea292d2c25d37d3 | Original frozen base; no learned reader/continued checkpoint |
| 5 | zsre | v0_live_C2 | full | 80ddc97cf168469a283ec56b482600ad92c546b7e915f4485be5ddc8158ab742 | Original frozen base; no learned reader/continued checkpoint |
| 6 | zsre | S1_LM | full | d6e808f0c225d826ce92cea4f38dda6ef970ff21a0f0f0b1d462b6bd72c03f99 | 6ef32487c4f4e2641ee0b5aba966651741788a98549c27292e6d40fa583992c6 |
| 7 | zsre | S1_literal | full | 6b43f8ffeb9b675b957cd9eccfbe5ed7e729f10cd2864c5d781b0c12c1d47736 | 7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5 |
| 8 | zsre | R1_learned_ff_v2 | incremental | 6a2686238d12521787d504e5c233ad8774e5b3a393b9b8bf602158daca138bdb | c5777b5bf0df754766463737f53f641f624de8bc98ac0420fd99bec8850730db |
| 9 | counterfact | R1_nonlearned | incremental | bc5ab233d75b07df969880daaf88bfe2c87c9d8433fcd20b2f7f47f0efaaac9b | a0e50ef72af48963062f8acabcf02ca66171d5d87f12cebf7074978a38a8317c |
| 10 | counterfact | v0_stable | full | 1a90ba465146cc7363e738c2f3179e61da1e730174246422ada8674617ff0977 | Original frozen base; no learned reader/continued checkpoint |
| 11 | counterfact | matched_update | full | 938fa83ce8455213f4e0dae29f0a890309fbbe9639d2aafc967c3870849006c2 | Original frozen base; no learned reader/continued checkpoint |
| 12 | counterfact | v0_live_C1 | full | 94531f55f922a66ba629ee1137694cac5673b82c54d4e4897643caaa4944ff5c | Original frozen base; no learned reader/continued checkpoint |
| 13 | counterfact | v0_live_C2 | full | 080c9aab0de015d3b5856adfb95dbd66cbf8c0340c5ac71d374566c15d1681fd | Original frozen base; no learned reader/continued checkpoint |
| 14 | counterfact | S1_LM | full | ecf973fb71b08ca1a88219366bc66e0cfd1cb24bed76703938ee6bc4fb99eba5 | 6ef32487c4f4e2641ee0b5aba966651741788a98549c27292e6d40fa583992c6 |
| 15 | counterfact | S1_literal | full | 7872c6bc94f24dede7a16108954704d4202da207f4ba1af1ddaaeaec135eb788 | 7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5 |
| 16 | counterfact | R1_learned_ff_v2 | incremental | 3526df269517f8ef4202ac1de79f94f164720675e6d48547615abad3f41235e7 | c5777b5bf0df754766463737f53f641f624de8bc98ac0420fd99bec8850730db |

Every receipt includes adapter/config/base identities, exact payload binding, expected output directory and checkpoints100/300. State hashes are outputs of those checkpoints, not guessed inputs. The two exact RevisionCap conditions use incremental integrity; all other classes use full. S1 uses the continued-NPZ constructor.

Commands below are owner execution commands, not CPU inspection commands. Stop on any nonzero exit and reconcile failure cost before an explicitly requested resume.

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-R1_nonlearned.recipe.json --manifest-sha256 88e1057ab589948eaf51fd46292276ef5b8ed6ecb8ad03e31917f424878ace32 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-v0_stable.recipe.json --manifest-sha256 ca13fe8b335228873edeb05548d027e88e3c2d7e0f42039592d6165f1cccbb91 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-matched_update.recipe.json --manifest-sha256 6fe37dc6aa241962a86218dcfb5518f9a180e39a7a4d4a14d7fe4dbe1b4d8f00 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-v0_live_C1.recipe.json --manifest-sha256 b3773723158c1ea149ca2c0816d7ca95b9cf93f6f3529a326ea292d2c25d37d3 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-v0_live_C2.recipe.json --manifest-sha256 80ddc97cf168469a283ec56b482600ad92c546b7e915f4485be5ddc8158ab742 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-S1_LM.recipe.json --manifest-sha256 d6e808f0c225d826ce92cea4f38dda6ef970ff21a0f0f0b1d462b6bd72c03f99 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-S1_literal.recipe.json --manifest-sha256 6b43f8ffeb9b675b957cd9eccfbe5ed7e729f10cd2864c5d781b0c12c1d47736 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-zsre-R1_learned_ff_v2.recipe.json --manifest-sha256 6a2686238d12521787d504e5c233ad8774e5b3a393b9b8bf602158daca138bdb --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-R1_nonlearned.recipe.json --manifest-sha256 bc5ab233d75b07df969880daaf88bfe2c87c9d8433fcd20b2f7f47f0efaaac9b --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-v0_stable.recipe.json --manifest-sha256 1a90ba465146cc7363e738c2f3179e61da1e730174246422ada8674617ff0977 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-matched_update.recipe.json --manifest-sha256 938fa83ce8455213f4e0dae29f0a890309fbbe9639d2aafc967c3870849006c2 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-v0_live_C1.recipe.json --manifest-sha256 94531f55f922a66ba629ee1137694cac5673b82c54d4e4897643caaa4944ff5c --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-v0_live_C2.recipe.json --manifest-sha256 080c9aab0de015d3b5856adfb95dbd66cbf8c0340c5ac71d374566c15d1681fd --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-S1_LM.recipe.json --manifest-sha256 ecf973fb71b08ca1a88219366bc66e0cfd1cb24bed76703938ee6bc4fb99eba5 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-S1_literal.recipe.json --manifest-sha256 7872c6bc94f24dede7a16108954704d4202da207f4ba1af1ddaaeaec135eb788 --execute
```

```bash
../venv/bin/python -m scripts.r1_64c_comparator_recipes run --manifest docs/tasks/R1-64c-counterfact-R1_learned_ff_v2.recipe.json --manifest-sha256 3526df269517f8ef4202ac1de79f94f164720675e6d48547615abad3f41235e7 --execute
```
