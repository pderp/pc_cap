# S3-03 grammar development matrix (replacement grammar; one realization, two orders; 8 tasks × 16 items)

| arm | order | ES | GS | RET-ES | RET-GS | LS | drift | accepted routes (1/2/3) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| C0 | 0 | 1.00 | 0.25 | 1.00 | 0.25 | 1.00 | 1.000 | 0/0/544 |
| C0 | 1 | 1.00 | 0.23 | 1.00 | 0.23 | 1.00 | 1.000 | 0/0/544 |
| C1 | 0 | 0.70 | 0.23 | 0.70 | 0.23 | 1.00 | 1.000 | 139/316/609 |
| C1 | 1 | 0.70 | 0.23 | 0.70 | 0.23 | 1.00 | 1.000 | 139/316/609 |
| C2 | 0 | 1.00 | 0.26 | 1.00 | 0.26 | 1.00 | 1.000 | 399/3/163 |
| C2 | 1 | 1.00 | 0.25 | 1.00 | 0.25 | 1.00 | 1.000 | 399/3/163 |
| CR | 0 | 0.91 | 0.24 | 0.91 | 0.24 | 1.00 | 1.000 | 131/152/196 |
| CR | 1 | 0.91 | 0.23 | 0.91 | 0.23 | 1.00 | 1.000 | 131/152/196 |

Order invariance across the two committed orders:

- C0: per-item immediate-ES equal on 1.00 of items; route counts equal: True
- C1: per-item immediate-ES equal on 1.00 of items; route counts equal: True
- C2: per-item immediate-ES equal on 1.00 of items; route counts equal: True
- CR: per-item immediate-ES equal on 1.00 of items; route counts equal: True

C2 routing versus tracing (D.10, descriptive):

- shared_2: C2 accepted routes {'1': 0.5241379310344828, '2': 0.020689655172413793, '3': 0.45517241379310347} over 290 deliveries; tracing's earliest restoring bank 2 (all banks restore: False); share at that bank 0.020689655172413793
- shared_1: C2 accepted routes {'1': 0.8926829268292683, '2': 0.0, '3': 0.1073170731707317} over 410 deliveries; tracing's earliest restoring bank 1 (all banks restore: True); share at that bank 0.8926829268292683
- private: C2 accepted routes {'1': 0.6511627906976745, '2': 0.0, '3': 0.3488372093023256} over 430 deliveries; tracing's earliest restoring bank 1 (all banks restore: True); share at that bank 0.6511627906976745

GS/RET-GS equal the frozen base's task accuracy (0.24–0.31): exact keys (SD-20) give no retrieval generalization on the grammar
