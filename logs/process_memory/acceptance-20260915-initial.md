# Process memory monitor: initial host acceptance

Observed 2026-09-15T20:24:43.576092+00:00. CPU only. Both user services were verified active; linger is enabled.

14 complete samples. Latest coverage: `{'visible': 445, 'sampled': 445, 'unreadable': 0, 'raced': 0, 'malformed': 0}`. Collection time range: 31.47–33.93 ms.

The systemd check reported monitor MemoryCurrent=10,944,512 bytes, MemoryPeak=11,083,776 bytes, CPUUsageNSec=189,117,000 and no restarts. These are a short acceptance observation, not a stress-test bound.

Installed tests: 12 passed in 0.10 s; Ruff passed; host systemd-analyze --user verify passed. The new host service is enabled; the original sysmon service remains running.

Pending: process-title command-label correction. The exact tested patch is in docs/tasks/process-memory-command-label.patch; existing-file permission was requested. Chrome may rewrite argv[0] with arguments, so this initial version can include a truncated process title in its label. Raw log evidence remains untouched.

## Source identities

- `scripts/process_memory_monitor.py`: `6b6035645cd673977535e82dc0330cfa6956e6c73bd5b47644417ce688aa6fdd`
- `scripts/pccap-process-memory.service`: `5eab01e115a4b37bb389567fb9d335e875bdfec36e2698f28bb788ca59a4ddbb`
- `tests/test_process_memory_monitor.py`: `c6b4122c0150a98c5b8e4f1b03912f95e76fd7191d06201ab330c14142fe92de`

## Report from the live host samples

```text
Process memory report — boot d53f420c-3b8e-4a9b-ba80-58e323dd49ed
Recorded window: 2026-09-15T20:22:29.749280+00:00 to 2026-09-15T20:24:39.748977+00:00 (14 samples, UTC)
Requested lookback: 300 seconds before this boot's last complete sample.
Minimum MemAvailable: 25569.6 MiB at 2026-09-15T20:24:29.748135+00:00
Maximum swap used: 0.0 MiB
Maximum PSI full avg10: memory 0.00%, IO 0.40%
Largest observed sample gap: 10.00 s; collection max 33.93 ms
Minimum sampled/visible process coverage: 100.0%
Alerts (sample counts): {}
Log read issues: {}; rows missing identity: 0
Host counter changes within the observed window: {"oom_kill": 0, "pgmajfault": 23, "pgscan_direct": 0, "pgscan_kswapd": 0, "pswpin": 0, "pswpout": 0}

Largest observed resident-memory consumers:
PID/start_ticks | peak RSS MiB | first→last RSS MiB | net MiB/min | peak swap MiB | samples | identity
59567/184163 | 1252.5 | 1252.5→1252.5 | +0.0 | 0.0 | 14 | swipl (ppid=59562, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/omegaclaw.service)
2244/2906 | 765.2 | 736.4→764.6 | +13.0 | 0.0 | 14 | /usr/bin/plasmashell (ppid=1322, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/session.slice/plasma-plasmashell.service)
4972/13760 | 612.7 | 445.9→551.2 | +48.6 | 0.0 | 14 | claude (ppid=3697, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.konsole-3480.scope/tab(3697).scope)
2109/2861 | 476.1 | 476.1→476.1 | +0.0 | 0.0 | 14 | /usr/bin/plasma-keyboard (ppid=2042, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/session.slice/plasma-kwin_wayland.service)
2042/2794 | 417.8 | 412.4→409.8 | -1.2 | 0.0 | 14 | /usr/bin/kwin_wayland (ppid=2028, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/session.slice/plasma-kwin_wayland.service)
21983/125479 | 380.0 | 379.9→379.8 | -0.0 | 0.0 | 14 | /opt/google/chrome/chrome (ppid=1322, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-com.google.Chrome-21983.scope)
2582/2992 | 328.9 | 328.9→328.9 | +0.0 | 0.0 | 14 | /usr/libexec/DiscoverNotifier (ppid=1322, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.discover.notifier@autostart.service)
22030/125508 | 313.1 | 312.9→312.9 | -0.0 | 0.0 | 14 | /opt/google/chrome/chrome --type=gpu-process --ozone-platform=wayland --render-node-override=/dev/dri/renderD128 --crashpad-handler-pid=21990 --enable-crash-reporter=40a46b29-b434-4290-a845-70d9b030121c, --change-stack-guard-on-fork=enable --gpu-preference (ppid=21998, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-google\x2dchrome@51f94eb073924ad1a30a08b2f1314900.service)
3059/3054 | 298.1 | 295.7→298.1 | +1.1 | 0.0 | 14 | /opt/Mattermost/mattermost-desktop (ppid=2937, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-mattermost\x2ddesktop@autostart.service)
22448/125853 | 274.8 | 274.8→273.7 | -0.5 | 0.0 | 14 | /opt/google/chrome/chrome --type=renderer --crashpad-handler-pid=21990 --enable-crash-reporter=40a46b29-b434-4290-a845-70d9b030121c, --change-stack-guard-on-fork=enable --ozone-platform=wayland --lang=en-US --num-raster-threads=4 --enable-main-frame-before (ppid=22001, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-google\x2dchrome@51f94eb073924ad1a30a08b2f1314900.service)

Largest positive net RSS increases (first to last observation of the same process):
PID/start_ticks | peak RSS MiB | first→last RSS MiB | net MiB/min | peak swap MiB | samples | identity
4972/13760 | 612.7 | 445.9→551.2 | +48.6 | 0.0 | 14 | claude (ppid=3697, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.konsole-3480.scope/tab(3697).scope)
2244/2906 | 765.2 | 736.4→764.6 | +13.0 | 0.0 | 14 | /usr/bin/plasmashell (ppid=1322, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/session.slice/plasma-plasmashell.service)
3059/3054 | 298.1 | 295.7→298.1 | +1.1 | 0.0 | 14 | /opt/Mattermost/mattermost-desktop (ppid=2937, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-mattermost\x2ddesktop@autostart.service)
3969/5309 | 242.1 | 238.4→239.7 | +0.6 | 0.0 | 14 | codex (ppid=3791, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.konsole-3480.scope/tab(3791).scope)
61295/220461 | 16.9 | 15.8→16.9 | +0.5 | 0.0 | 14 | /home/derp/cap/venv/bin/python /home/derp/cap/pc_cap/scripts/process_memory_monitor.py (ppid=1322, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/pccap-process-memory.service)
61600/224265 | 6.6 | 5.9→6.6 | +0.5 | 0.0 | 10 | systemd-userwork: waiting... (ppid=653, uid=0, cgroup=/system.slice/systemd-userdbd.service)
61601/224265 | 6.6 | 5.9→6.6 | +0.5 | 0.0 | 10 | systemd-userwork: waiting... (ppid=653, uid=0, cgroup=/system.slice/systemd-userdbd.service)
61711/225275 | 6.7 | 6.1→6.7 | +0.5 | 0.0 | 9 | systemd-userwork: waiting... (ppid=653, uid=0, cgroup=/system.slice/systemd-userdbd.service)
3037/3052 | 114.4 | 114.3→114.4 | +0.1 | 0.0 | 14 | /opt/Mattermost/mattermost-desktop (ppid=2937, uid=1001, cgroup=/user.slice/user-1001.slice/user@1001.service/app.slice/app-mattermost\x2ddesktop@autostart.service)
1125/580 | 39.1 | 39.0→39.1 | +0.0 | 0.0 | 14 | /usr/bin/abrt-dump-journal-core (ppid=1, uid=0, cgroup=/system.slice/abrt-journal-core.service)

Largest observed cgroup memory.current peaks (MiB; nested groups overlap):
6433.7 | /user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.konsole-3480.scope/tab(3697).scope | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
834.4 | /user.slice/user-1001.slice/user@1001.service/app.slice/app-google\x2dchrome@51f94eb073924ad1a30a08b2f1314900.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
740.6 | /user.slice/user-1001.slice/user@1001.service/app.slice/omegaclaw.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
718.8 | /system.slice/abrt-journal-core.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
696.3 | /user.slice/user-1001.slice/user@1001.service/app.slice/app-mattermost\x2ddesktop@autostart.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
631.3 | /user.slice/user-1001.slice/user@1001.service/session.slice/plasma-plasmashell.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
472.5 | /user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.konsole-3480.scope/tab(3791).scope | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
445.1 | /user.slice/user-1001.slice/user@1001.service/session.slice/plasma-kwin_wayland.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
310.2 | /user.slice/user-1001.slice/user@1001.service/background.slice/akonadi_control.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}
302.8 | /user.slice/user-1001.slice/user@1001.service/app.slice/app-org.kde.discover.notifier@autostart.service | memory.events delta={'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0, 'sock_throttled': 0}

Last complete samples: UTC | available MiB | swap used MiB | sampled/visible
2026-09-15T20:23:49.748248+00:00 | 25723.7 | 0.0 | 445/445
2026-09-15T20:23:59.747872+00:00 | 25699.5 | 0.0 | 445/445
2026-09-15T20:24:09.747705+00:00 | 25653.8 | 0.0 | 445/445
2026-09-15T20:24:19.748185+00:00 | 25582.5 | 0.0 | 445/445
2026-09-15T20:24:29.748135+00:00 | 25569.6 | 0.0 | 445/445
2026-09-15T20:24:39.748977+00:00 | 25598.0 | 0.0 | 445/445

Interpretation: RSS is approximate and shared pages appear in multiple processes; do not sum it.
VmSwap excludes swapped shared memory. A missing measurement is not zero.
Net growth is descriptive, not a leak diagnosis; processes may start/exit within this window.
Coverage counts only processes visible in the monitor's PID namespace; inaccessible processes are reported.
A hard freeze can prevent final writes. Logs alone cannot prove a cause or prevent exhaustion.
```
