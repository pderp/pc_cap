# Process memory monitoring

This companion to Claude's existing sysmon service records every accessible process
every 10 seconds, using only Python's standard library and Linux proc/cgroup files.
It does not import JAX, query NVIDIA, execute models, or terminate other processes.

The motivation is concrete: the final section of
[Stage 2 notes](R1_stage2_notes.md) reports the September 15 tri6 trainer growing
from about 6.8 to 22.7 GB RSS, with available RAM falling to about 0.4 GB and 8 GB
swap full. The associated evidence is in
[the existing system log](../logs/sysmon/sysmon-20260915.log).
That supports host-memory pressure as a failure mechanism. The notes attribute
the growth to accumulating XLA executables for variable prefix lengths; process
memory measurements alone cannot distinguish executable caches from other
allocations inside Python. The earlier hangs were not recorded at this resolution.

## What is recorded

[scripts/process_memory_monitor.py](../scripts/process_memory_monitor.py) has
two commands, record and report. The recorder saves:

- UTC timestamps, monotonic sampling times, boot UUID, session UUID, PID namespace,
  and a versioned column schema. Process identity is PID plus start ticks within a
  boot; a reused PID does not inherit the old process's growth.
- Every visible process's RSS, resident high-water mark, anonymous/file/shared RSS,
  private swap, virtual memory, threads and cumulative major page faults.
- Parent PID, UID, executable, process name, cgroup, and a deliberately limited
  command label. Python labels include a script/module and allowlisted --tag,
  --run-name, --run-id and --seed selectors. Arbitrary arguments, inline Python
  source and environment variables are not collected. Labels can still contain
  identifying project/run names; files are created with mode 0600.
- Available host RAM, swap, cache and selected kernel memory counters; memory,
  CPU and IO pressure; cumulative swap/page-fault/OOM counters; and accessible
  cgroup-v2 memory usage, limits and events.
- Coverage counts, missing fields as null, collection time and pressure alerts.
  Low available memory defaults to 3 GiB, swap pressure to 80% used, and full
  memory-stall pressure to 1% avg10. These alerts are evidence, not a kill policy.

Linux reports RSS approximately; shared resident pages appear in multiple
processes. Do not add RSS values to estimate unique physical RAM. VmSize is
virtual address space, and VmSwap excludes swapped shared memory.
See the [kernel proc documentation](https://docs.kernel.org/filesystems/proc.html).
The logger deliberately avoids scanning smaps/page tables for proportional memory
on every sample. PSI records time stalled on a resource; its full avg10 is a
ten-second average, not a count of failed allocations.
See the [kernel PSI documentation](https://docs.kernel.org/accounting/psi.html).
Cgroup memory.current includes accounted group memory; hierarchical groups and
their event counters can overlap, so those rows should not be summed either.
See the [cgroup-v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html).

## Durable logs and disk limits

Live logs go in pc_cap/logs/process_memory/memory-*.jsonl, excluded from Git by a
new directory-local .gitignore. Each run and each approximately 64 MiB segment
gets a unique, exclusively created file. Historical files are never reopened for
writing, truncated, removed, or compressed by the monitor. Unchanged process
identity metadata is omitted from later samples in a segment; every segment
begins with a complete identity inventory. The included reader reconstructs it.

Each complete sample is flushed and fsynced. New segment directory entries are
also fsynced. This improves recovery after an abrupt reboot, but a hard freeze,
storage failure, or power loss may still prevent the final samples reaching disk.
A report counts and skips incomplete final records/headers and malformed JSON
lines, and refuses unknown schemas. A damaged complete header requires inspection.

The defaults are a 16 GiB total budget for memory-*.jsonl in this directory and
a 1 GiB free-disk floor. Reaching either stops recording with a clear error;
the service does not restart on storage/configuration exit 73 or singleton-lock
exit 74. No silent evidence deletion. Check service status and archive old logs
before the budget fills; the retention duration depends on process count and
turnover, so it is not a promised number of days. An active directory is locked
to one writer. Each sample is limited to 32 MiB.

## Host service and use

The new [service unit](../scripts/pccap-process-memory.service) runs independently
of pccap-sysmon.service. It uses the existing venv with bytecode writes disabled.
MemoryHigh=192M and MemoryMax=256M apply only to the monitor. It has no dependency
on experiment execution and records at login; this host's existing user linger
configuration is what also permits recording without an interactive login.

Installation creates a new symlink; ln refuses if that name already exists:

~~~sh
ln -s /home/derp/cap/pc_cap/scripts/pccap-process-memory.service /home/derp/.config/systemd/user/pccap-process-memory.service
systemctl --user daemon-reload
systemctl --user enable --now pccap-process-memory.service
systemctl --user status pccap-process-memory.service
~~~

The service must run on the host: a coding sandbox's proc view only contains its
own processes, even when meminfo shows host totals. A sampled/visible percentage
cannot certify visibility outside that namespace. Host acceptance evidence belongs
in logs/process_memory/acceptance-*.md.

Read the last 30 recorded minutes, or the last recorded boot before this boot:

~~~sh
cd /home/derp/cap/pc_cap
../venv/bin/python -B scripts/process_memory_monitor.py report
../venv/bin/python -B scripts/process_memory_monitor.py report --boot previous --window 1800
../venv/bin/python -B scripts/process_memory_monitor.py report --boot current --window 300 --top 20
../venv/bin/python -B scripts/sysmon_report.py --before-boot -1 --window 1800
~~~

Exact recorded boot UUIDs are also accepted. The window ends at the chosen boot's
last complete memory sample, which may precede the crash. The report ranks
peak RSS and positive net RSS growth, shows private swap, identifies jobs and
cgroups, summarizes host pressure/counter changes, and displays the last six
samples. Rates are first-to-last changes over each process's observed lifetime
within the window, not fitted leak slopes. Long gaps, brief processes between
samples, inaccessible processes and the final unrecorded moments limit inference.
Old crashes cannot be reconstructed from this new logger.

For a finite smoke check, choose a fresh subdirectory so it cannot conflict
with the live service:

~~~sh
../venv/bin/python -B scripts/process_memory_monitor.py record --samples 3 --interval 1 --log-dir logs/process_memory/manual-smoke-CHOOSE-UNIQUE-NAME
~~~

To stop/restart the service, use systemctl --user stop/start
pccap-process-memory.service. Continuous logging is explicitly requested; the
logger only writes its own newly created segments and never edits project source
or previously closed log segments. Existing logger, trainer, plans and task board
remain untouched.

## Validation and next safeguards

The synthetic CPU tests cover command identification, PID reuse and disappearing
processes, permissions, missing data, pressure and cgroups, exclusive writers,
per-sample fsync, independent segments, storage refusal, growth calculations,
boot/window selection, identity reconstruction, and truncated/corrupt log recovery:

~~~sh
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q -p no:cacheprovider tests/test_process_memory_monitor.py
../venv/bin/ruff check --no-cache scripts/process_memory_monitor.py tests/test_process_memory_monitor.py
~~~

The monitor is diagnostic. To reduce recurrence, the orchestrator's bounded
prefix-length compilation and training memory guard should be verified on a
single bounded run while watching RSS and swap growth. A guard evaluated between
training steps cannot stop a rapid spike inside compilation. An explicit memory
ceiling for each training job could offer an additional boundary, but choosing it
requires a measured working set and an agreed checkpoint/termination policy.
Neither trainer changes nor a job-killing policy are applied by this addition.
