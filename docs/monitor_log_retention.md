# Forty-eight-hour retention for both monitoring services

Requested by Charlie on September 15, 2026. This is the current retention policy
for raw monitoring files; it supersedes the earlier indefinite-evidence-retention
description in process_memory_monitor.md. The 16 GiB emergency monitor quota and
1 GiB disk-free floor remain secondary safeguards.

The new hourly pccap-monitor-retention.timer runs
[scripts/monitor_log_retention.py](../scripts/monitor_log_retention.py) on the host.
The helper identifies expired, closed files and writes a configuration containing
only their explicit paths. Native logrotate then uses rotate 0 and nocreate to
discard those files without retaining another archive. It uses an independent
configuration and /dev/null state, with a helper lock for concurrent invocations.
The system-wide logrotate policy is unaffected.

Both existing loggers already create segments, so another rotation of their
active files is unnecessary. Native maxage is tied to rotation processing; an
elapsed-time selection step gives the intended cutoff for these existing
date/session filenames. See the
[logrotate manual](https://github.com/logrotate/logrotate/blob/main/logrotate.8.in).

The cutoff is **48 hours since a file's last write**, checked hourly. The helper
protects files open in accessible processes of this user, today's sysmon file,
symlinks, hardlinks, foreign-owned files and unrelated filenames. It refuses if it
cannot inspect descriptors of a recognized running logger. File identity, size
and modification time are checked again before logrotate executes.

This is whole-file retention, not removal of individual old lines: a sample
inside a long segment can be older than 48 hours until that entire segment expires.
Sysmon segments are daily; memory segments are approximately 64 MiB. An expired
closed file normally disappears at the next hourly check, within about 49 hours
of its last write while the machine and timer are running. Persistent=true catches
missed calendar activations when the user service manager starts again. Open or
otherwise protected files are retained until eligible.

Only these direct children of the repository's log directories are eligible:

- logs/sysmon/sysmon-YYYYMMDD.log
- logs/process_memory/memory-*.jsonl
- A matching .1 intermediate left by an interrupted logrotate deletion.

Incident reports, acceptance notes, experiment results, scripts, tests and other
documentation are outside this policy. The logger scripts and their sample
intervals do not need to change for expiry.

At the initial observed rate (23.6 MB/hour combined), expect roughly 1.1–1.3 GB of
raw retained monitoring logs, allowing for whole segments and the hourly sweep.
Actual usage follows process count and turnover. Each expiry run also creates a
small, Git-ignored directory under logs/monitor_retention/ with its plan,
generated logrotate.conf, result, and logrotate output if anything was eligible.
These small operational receipts are not part of the two raw-log expiry rules.

## Operation

~~~sh
systemctl --user status pccap-monitor-retention.timer
systemctl --user list-timers pccap-monitor-retention.timer
systemctl --user start pccap-monitor-retention.service
journalctl --user -u pccap-monitor-retention.service --since today
~~~

Read-only selection preview (it creates a new plan/report directory):

~~~sh
cd /home/derp/cap/pc_cap
../venv/bin/python -B scripts/monitor_log_retention.py
~~~

The --apply option requires this machine's host PID namespace. A coding sandbox
cannot reliably identify host processes holding log files open. The installed
user service provides the correct view. The helper calls /usr/bin/logrotate
from the installed PATH and does not invoke GPU tools or import JAX.

Installation uses new symlinks and a new user timer:

~~~sh
ln -s /home/derp/cap/pc_cap/scripts/pccap-monitor-retention.service /home/derp/cap/pc_cap/scripts/pccap-monitor-retention.timer /home/derp/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now pccap-monitor-retention.timer
systemctl --user start pccap-monitor-retention.service
~~~

Seven synthetic tests exercise the 48-hour boundary, real logrotate deletion of
both file families, open files, changed files, symlinks/hardlinks, preview mode,
and unsafe path refusal. They use disposable fixtures, never the live monitor
directories:

~~~sh
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m pytest -q -p no:cacheprovider tests/test_monitor_log_retention.py
~~~

A companion storage-accounting correction is prepared in
[the edit request](tasks/process-memory-retention-quota-edit-request.md). It makes
the process monitor recount retained bytes at segment boundaries, so externally
expired logs do not remain charged to its lifetime byte counter. That source edit
requires the lead's separate existing-file permission.
