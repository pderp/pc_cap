#!/bin/bash
# OS-level lockup forensics (requested by the lead after two hard reboots on 2026-09-15).
# Every INTERVAL seconds append one line to logs/sysmon/sysmon-YYYYMMDD.log with: time, load, memory, swap, PSI stalls,
# GPU utilisation/memory/temperature/power/clock/throttle reasons, the GPU compute processes, the top CPU and RSS
# processes, and new kernel lines matching GPU/OOM/lockup patterns. Lines are flushed to disk immediately so the last
# seconds before a hang survive a hard reboot. Runs as a systemd user service (see scripts/sysmon.service).
INTERVAL=${SYSMON_INTERVAL:-10}
DIR=${SYSMON_DIR:-/home/derp/cap/pc_cap/logs/sysmon}
mkdir -p "$DIR"
LAST_K=$(date +%s)
while true; do
  TS=$(date '+%Y-%m-%dT%H:%M:%S')
  F="$DIR/sysmon-$(date +%Y%m%d).log"
  LOAD=$(cut -d' ' -f1-3 /proc/loadavg)
  MEM=$(awk '/MemTotal/{t=$2}/MemAvailable/{a=$2}/SwapTotal/{st=$2}/SwapFree/{sf=$2}END{printf "mem_avail_mb=%d mem_total_mb=%d swap_used_mb=%d", a/1024, t/1024, (st-sf)/1024}' /proc/meminfo)
  PSI=$(awk 'NR==1{printf "psi_cpu=%s ", $2} ' /proc/pressure/cpu 2>/dev/null; awk 'NR==2{printf "psi_mem_full=%s ", $2}' /proc/pressure/memory 2>/dev/null; awk 'NR==2{printf "psi_io_full=%s", $2}' /proc/pressure/io 2>/dev/null)
  GPU=$(timeout 5 nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,clocks.sm,clocks_throttle_reasons.active,pstate --format=csv,noheader,nounits 2>&1 | head -1 | tr -d ' ' | sed 's/,/ /g')
  [ -z "$GPU" ] && GPU="nvidia-smi_no_response"
  GPROCS=$(timeout 5 nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits 2>/dev/null | tr -d ' ' | tr '\n' ';')
  TOPCPU=$(ps -eo pid,pcpu,rss,comm --sort=-pcpu | awk 'NR>1 && NR<=4{printf "%s:%s:%.1f%%:%dMB;", $1, $4, $2, $3/1024}')
  TOPRSS=$(ps -eo pid,rss,comm --sort=-rss | awk 'NR>1 && NR<=3{printf "%s:%s:%dMB;", $1, $3, $2/1024}')
  NOW=$(date +%s)
  KMSG=$(journalctl -k --since "@$LAST_K" --no-pager -o short-iso 2>/dev/null | grep -iE "xid|nvrm|oom|out of memory|hung task|lockup|rcu_|thermal|throttl|mce|nmi|blocked for more" | tail -3 | tr '\n' '|' | cut -c1-400)
  LAST_K=$NOW
  echo "$TS load=$LOAD $MEM $PSI gpu[util%,memMB,totMB,C,W,MHz,throttle,pstate]=$GPU gpu_procs=$GPROCS top_cpu=$TOPCPU top_rss=$TOPRSS kmsg=$KMSG" >> "$F"
  sync -f "$F" 2>/dev/null || sync
  sleep "$INTERVAL"
done
