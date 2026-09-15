# Memory monitor command-label correction

Host verification found that Chrome rewrites argv[0] to contain its process title and arguments. The monitor should retain only the first word of argv[0], then its existing allowlisted Python selectors. This keeps the documented restricted command policy accurate.

The attached `process-memory-command-label.patch` changes two lines into four in `scripts/process_memory_monitor.py`. Three in-memory regression checks passed: rewritten title with a secret flag omitted; inline Python omitted; training script and tag retained. Approval is requested because the lead requires permission before editing any existing file. After applying it, restart only pccap-process-memory.service and rerun its tests. Prior log evidence is preserved.
