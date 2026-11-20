#!/usr/bin/env bash
# Usage: harness/env/quiet.sh on|off
# on: closes desktop apps and stops background work that can burst during a
# run (indexer, updates, docker), until the next reboot or `off`.
# The terminal, this session and the pinned browsers are never touched.
set -euo pipefail

if [[ $# -ne 1 || ($1 != on && $1 != off) ]]; then
  echo "usage: $0 on|off" >&2
  exit 2
fi

repository=$(cd "$(dirname "$0")/../.." && pwd -P)
pinned_browsers="$repository/harness/browsers/"

apps=(zen firefox chrome chromium code cursor discord slack spotify telegram-desktop thunderbird obsidian steam nautilus evince loupe)
system_units=(docker.socket docker.service containerd.service snapd.socket snapd.service
  apt-daily.timer apt-daily-upgrade.timer unattended-upgrades.service fwupd.service
  packagekit.service man-db.timer motd-news.timer)
user_units=(localsearch-3.service evolution-addressbook-factory.service evolution-calendar-factory.service
  evolution-source-registry.service speech-dispatcher.service
  snap.firmware-updater.firmware-notifier.service)

is_pinned_browser() {
  [[ $(readlink -f "/proc/$1/exe" 2>/dev/null) == "$pinned_browsers"* ]]
}

session_ancestors() {
  local pid=$$
  while ((pid > 1)); do
    echo "$pid"
    pid=$(awk '{print $4}' "/proc/$pid/stat" 2>/dev/null || echo 1)
  done
}

mapfile -t protected < <(session_ancestors)

is_protected() {
  [[ " ${protected[*]} " == *" $1 "* ]]
}

close_apps() {
  local name pid closed=()
  for name in "${apps[@]}"; do
    for pid in $(pgrep -x "$name" 2>/dev/null || true); do
      is_pinned_browser "$pid" && continue
      is_protected "$pid" && continue
      kill -TERM "$pid" 2>/dev/null && closed+=("$name:$pid")
    done
  done
  echo "closed apps: ${closed[*]:-none}"
}

state=${XDG_RUNTIME_DIR:-/tmp}/ppc-quiet.state

active_system_units() {
  local unit
  for unit in "${system_units[@]}"; do
    systemctl is-active --quiet "$unit" && echo "system $unit"
  done
}

active_user_units() {
  local unit
  for unit in "${user_units[@]}"; do
    systemctl --user is-active --quiet "$unit" && echo "user $unit"
  done
}

# Claude Code processes are stopped (SIGSTOP), not killed, for the whole campaign, and
# continued by "off". A stopped process keeps its children running, so a campaign Claude started
# goes on; its output must go to a file, not to Claude's pipe. QUIET_KEEP_CLAUDE=1 keeps them running.
stop_claude() {
  local pid stopped=()
  if [[ ${QUIET_KEEP_CLAUDE:-0} == 1 ]]; then
    echo "claude: kept running (QUIET_KEEP_CLAUDE=1)"
    return
  fi
  for pid in $(pgrep -x claude 2>/dev/null || true); do
    grep -qx "claude $pid" "$state" 2>/dev/null && continue
    kill -STOP "$pid" 2>/dev/null && echo "claude $pid" >>"$state" && stopped+=("$pid")
  done
  echo "stopped claude: ${stopped[*]:-none} (continue by hand: kill -CONT <pid>)"
}

continue_claude() {
  local pid
  for pid in $(units_of claude); do
    # Only a PID that is still a Claude Code process: the PID may have been reused.
    [[ $(cat "/proc/$pid/comm" 2>/dev/null) == claude ]] && kill -CONT "$pid" 2>/dev/null || true
  done
}

units_of() {
  awk -v kind="$1" '$1 == kind {print $2}' "$state"
}

if [[ $1 == on ]]; then
  close_apps
  if [[ ! -e $state ]]; then
    { active_system_units; active_user_units; } >"$state" || true
  fi
  mapfile -t system_active < <(units_of system)
  mapfile -t user_active < <(units_of user)
  systemctl --user mask --runtime "${user_units[@]}" >/dev/null 2>&1 || true
  if ((${#user_active[@]})); then
    systemctl --user stop "${user_active[@]}" 2>/dev/null || true
  fi
  if ((${#system_active[@]})); then
    sudo -n systemctl stop "${system_active[@]}"
  fi
  echo "stopped: ${system_active[*]} ${user_active[*]}"
  stop_claude
  echo "busiest processes now:"
  ps -eo pcpu,rss,comm --sort=-pcpu | head -8
else
  [[ -e $state ]] || { echo "quiet mode is not on"; exit 0; }
  mapfile -t system_active < <(units_of system)
  mapfile -t user_active < <(units_of user)
  systemctl --user unmask --runtime "${user_units[@]}" >/dev/null 2>&1 || true
  if ((${#system_active[@]})); then
    sudo -n systemctl start "${system_active[@]}" || true
  fi
  if ((${#user_active[@]})); then
    systemctl --user start "${user_active[@]}" 2>/dev/null || true
  fi
  continue_claude
  rm -f "$state"
  echo "started again: ${system_active[*]} ${user_active[*]}"
fi
