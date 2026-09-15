# Monitor retention acceptance

Observed 2026-09-15T22:49:42.147566+00:00.

- Hourly pccap-monitor-retention.timer is enabled and active; the first host service invocation returned success (exit 0).
- The first invocation selected no files: sysmon’s current day and the open memory segment were protected, and the remaining segment was younger than 48 hours.
- Host service measurements: peak memory 8,744,960 bytes; CPU 43,858,000 ns. Six unrelated same-user processes denied descriptor access; recognized logger descriptors remained readable.
- Both original monitoring services remained active.
- Charlie approved the quota-accounting correction; it is applied and the memory monitor has been restarted. Deleted closed segments are recounted at the next segment boundary.
- Installed verification: 24 monitor/retention tests passed in 0.15 s, including actual logrotate deletion on disposable fixtures and budget release after expiry. Ruff passed. The separate R1-68b driver tests also passed (28 combined tests before adding the two quota tests).

Policy: expire whole closed log files more than 48 hours after their last write, checked hourly; protected/open files are retained. This is not a strict per-line 48-hour ceiling. Daily sysmon files and approximately 64 MiB memory segments remain independently readable until they expire. Raw incident evidence is intentionally subject to the requested retention limit; Markdown reports are outside its filename rules.

First/most recent expiry receipt: `logs/monitor_retention/run-20260915T220021.508536Z-b959a887`, status `ok`.

Source identities:

- `scripts/monitor_log_retention.py`: `7d7575e003e49211eb7304a292a2cb2ce03f4bb49ab0f9063d43043a116c139a`
- `scripts/pccap-monitor-retention.service`: `1842b7cd087c67531914cf87ea8d70138e3b116d0bc39887c13ee0e16cc125eb`
- `scripts/pccap-monitor-retention.timer`: `08758b3b9d9343865256e6c532e59948d706d367de59958896fea2488f5e4045`
- `scripts/process_memory_monitor.py`: `c5043e77f0258f92fcc18643305c7795eeb9817aa8bcee596e60328c0164acf8`
