# Storage accounting after log expiry

The monitor currently keeps a running byte total for its entire process lifetime. When the new, requested logrotate job deletes expired segments, that counter does not shrink; it could eventually stop at 16 GiB even though retained logs occupy far less disk space.

The exact patch in process-memory-retention-quota.patch recounts files on disk at each segment boundary and handles a file disappearing during a retention scan. Two in-memory regression checks passed, including deleting a closed test segment near the configured budget and successfully continuing recording.

Permission is requested only to apply this existing-file correction to scripts/process_memory_monitor.py and restart its service. The retention helper, timer, service, configuration receipts, tests and documentation are new files.
