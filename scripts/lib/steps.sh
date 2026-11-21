# shellcheck shell=bash
# Resumable steps of one stage of a measuring session. Sourced by scripts/session.sh, not run.
# A step runs once: its output goes to a log, and a done mark makes the next call skip it. A
# failed step stops the stage, and the next call starts again at that step.

is_dry_run() { [[ "${RUN_DRY:-0}" == 1 ]]; }

log() { printf '%s  %s\n' "$(date -u '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$SESSION/progress.log"; }

step() {
  local name="$1"
  shift
  if is_dry_run; then
    printf '%-28s %s\n' "$name" "$*"
  elif [[ -e "$SESSION/$name.done" ]]; then
    log "skip   $name"
  else
    log "start  $name"
    "$@" >"$SESSION/$name.log" 2>&1 || {
      log "failed $name: see $SESSION/$name.log"
      exit 1
    }
    touch "$SESSION/$name.done"
    log "done   $name"
  fi
}
