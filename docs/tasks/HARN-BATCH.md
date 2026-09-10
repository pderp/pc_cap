# HARN-BATCH Batched cap-on evaluation with sequential-decoder parity
status: done
agent: orchestrator   started: 2026-09-10T09:30:00Z   finished: 2026-09-10T03:40:10Z
commit: (uncommitted; lead commits)
inputs used: S2-06 first-pass throughput (wall 3-9 s/edit vs 0.2-0.7 s/edit accelerator: host dispatch per forward dominates the E.2 token-by-token evaluation); PDF E.2 ("A caching optimization may be reported separately only after parity with these semantics is verified"); HARN-C2 runner
outputs: gpt2_jax.{_head_rows,forward_batch_jit,forward_from_batch_jit} (last-row logits; vmapped cap-on kernels), BPBase.{forward(last_only),forward_from(last_only),forward_batch,forward_from_batch}, Cap.{edited_forward(full=),predict(full=),edited_forward_batch}, decode.greedy_decode_batch_cap, runs.Evaluator batched items/rescoring/locality/drift, tests/cap/test_batch_parity.py, results/S0/controls/harn_batch_parity.json
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/cap/test_batch_parity.py -m gpu && /home/derp/cap/venv/bin/python -m pccap.cli run --stage S3 --arm C2 --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s3_smoke.json
verify output: parity: 28 prompts (12 learned-pool prompts of which 8 learned into a C1 cap with firing slots, 10 paraphrases, 10 unrelated), 0 token mismatches between the batched cap-on decoder and the sequential reference decoder; S3 C2 smoke (20 items) wall 108 s -> 40 s with identical metrics (ES 1.0, GS 0.8, RET-ES 0.95, RET-GS 0.7, LS 1.0, drift ratio 1.0)
done-when check: semantics unchanged (full prefix recompute per step, cap writes only at the current prediction position, live sequential bank retrieval, stop at newline/EOS, read-only with hash assertion): PASS by construction and parity test; identity controls after the last-row path: PASS (cap-off identity exact on full logits; last-row vs full-row difference <= 1e-3, recorded in test_cap_core); every batched call charged to the query column (B forwards per call): PASS
cost: gpu_seconds=120 wall_seconds=3600 peak_mem_mib=2000
deviations: the last-row head projection ([d]@[d,V]) is a different GEMM shape than the full head ([T,d]@[d,V]); rows agree within fp32 GEMM tolerance (< 1e-3), and all identity assertions compare like-for-like paths. Learning (update_item) is unchanged and sequential.
unresolved: none
questions for lead: none
