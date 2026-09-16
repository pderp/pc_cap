# Memory monitor command-label correction: host acceptance

The approved correction was already present in Claude’s commit df22f12 when Codex attempted to apply it. Codex therefore preserved the existing change, added three regression cases in tests/test_process_memory_command_label.py, and restarted pccap-process-memory.service.

Validation: 15 tests passed in 0.11 s; Ruff passed. The new host session starts 2026-09-15T20:26:39.540682+00:00 and its first snapshot records {'visible': 452, 'sampled': 452, 'unreadable': 0, 'raced': 0, 'malformed': 0}. Chrome labels in this snapshot contain no argument flags. The prior session’s files remain intact.

Current source SHA256: `6b6035645cd673977535e82dc0330cfa6956e6c73bd5b47644417ce688aa6fdd`. Current session: `7d1d21d84be34048a47ef02b014a6962`.

Log-volume observation at 2026-09-15 20:36 UTC: 85 memory samples across two sessions; 83 steady-state samples averaged 65,066 bytes each. At the configured 10-second interval that is 23,423,851 bytes/hour. Sysmon averaged 441.9 bytes per sample over 898 seconds, or 157,702 bytes/hour at its observed cadence. Combined: 23.58 MB/hour (22.49 MiB/hour), 0.566 GB/day, and 13.58 GB over 24 days. The new monitor’s 16 GiB quota lasts about 30.6 days at this short-window rate. Each observed initial full-identity sample was about 151 KB. These are file-growth estimates; physical disk writes include filesystem overhead, and process count/turnover can change the rate.
