#!/bin/sh
# setup.sh            install a desk (shows what it will do, asks first)
# setup.sh --uninstall NAME   switch the desk's timers off and delete them
# Run it from inside the kit folder. It never asks for your password.

kit_src=$(cd "$(dirname "$0")" && pwd)
agents="$HOME/Library/LaunchAgents"
uid=$(id -u)

# --- Uninstall: stop and delete this desk's four timers. Your desk folder is left alone. ---
if [ "$1" = "--uninstall" ]; then
  [ -n "$2" ] || { echo "usage: sh setup.sh --uninstall NAME"; exit 2; }
  for job in claude codex watchdog keepawake; do
    plist="$agents/com.localdesk.$2.$job.plist"
    launchctl bootout "gui/$uid" "$plist" 2>/dev/null
    rm -f "$plist"
  done
  echo "Timers for '$2' are off. Delete ~/Desks/$2 yourself when you no longer need it."
  exit 0
fi

# --- Read the options. Typing them is optional: Claude Code passes them for you (NEW-DESK.md). ---
# Usage: sh setup.sh [--name NAME] [--goal "TEXT"] [--folder PATH] [--yes]
usage='Usage: sh setup.sh [--name NAME] [--goal "TEXT"] [--folder PATH] [--yes]'
name=""; goal=""; folder=""; yes=""
while [ $# -gt 0 ]; do
  case "$1" in
    --name|--goal|--folder)
      case "$2" in ""|--*) echo "$1 needs a value. $usage"; exit 2 ;; esac
      [ $# -ge 2 ] || { echo "$1 needs a value. $usage"; exit 2; }
      case "$1" in --name) name=$2 ;; --goal) goal=$2 ;; *) folder=$2 ;; esac
      shift ;;
    --yes) yes=1 ;;
    *) echo "Unknown option '$1'. $usage"; exit 2 ;;
  esac
  shift
done
if [ -z "$name" ]; then printf "Name for this desk (letters, digits, dashes): "; read -r name; fi
case "$name" in ""|*[!A-Za-z0-9-]*) echo "Use only letters, digits and dashes."; exit 2 ;; esac
desk="$HOME/Desks/$name"
kit="$HOME/DeskKit"
[ -e "$desk" ] && { echo "$desk already exists. Pick another name."; exit 2; }
command -v python3 >/dev/null && command -v git >/dev/null || { echo "Need python3 and git (Terminal: xcode-select --install)."; exit 2; }
# The optional work folder (a project the agents may change) must be an existing git repo, so every change can be undone.
if [ -n "$folder" ]; then
  [ -d "$folder/.git" ] || { echo "Work folder '$folder' must be an existing git project (a folder with .git inside)."; exit 2; }
  [ -z "$(git -C "$folder" status --porcelain)" ] || { echo "'$folder' has uncommitted changes. Commit or stash them first."; exit 2; }
  folder=$(cd "$folder" && pwd)
  # Never reuse an old branch: a desk with this name may have existed before.
  git -C "$folder" rev-parse --verify -q "refs/heads/desk/$name" >/dev/null && { echo "'$folder' already has a branch desk/$name. Pick another desk name."; exit 2; }
fi

cat <<EOF

This will create:
  $desk/        your desk: goal, to-do list, messages, a private git history (stays on this Mac)
  $kit/         the scripts the timers run (shared by all your desks; installing again replaces them)
  4 timers in $agents/ :
     Claude at :00 and :30, Codex at :15 and :45, a watchdog every 10 minutes, and a keep-awake
${folder:+Work folder: $folder
  The agents may change files there, but only on a new branch called desk/$name.
  They never push, merge or deploy. (Does your employer allow this folder to be used?)
}It will not touch anything else.
EOF
if [ -z "$yes" ]; then
  printf "Type yes to continue: "
  read -r answer
  [ "$answer" = "yes" ] || { echo "Nothing was written."; exit 0; }
fi

# --- Make the desk folder and its starting files ---
mkdir -p "$desk/status" "$desk/work" "$desk/_state" "$kit" "$agents"
[ "$kit_src" = "$kit" ] || cp "$kit_src/setup.sh" "$kit_src/run-agent.sh" "$kit_src/watchdog.py" "$kit_src/PROTOCOL-LITE.md" "$kit_src/NEW-DESK.md" "$kit/"
cp "$kit/PROTOCOL-LITE.md" "$desk/"
cat > "$desk/BRIEF.md" <<EOF
# Goal
${goal:-(Replace this line with what "done" looks like.)}

Work folder: ${folder:-none}

# Limits
Only change this desk folder${folder:+ and the work folder above (on branch desk/$name only)}. Never push, merge or deploy.
No company code, customer data, passwords or private documents in the desk.
EOF
printf '# Messages\n\nNew messages go at the bottom. Never edit old ones.\n' > "$desk/MESSAGES.md"
# STATE.json is made by Python so that quotes in your goal can't break it.
python3 -c '
import json, sys
goal = sys.argv[1] or "Replace this with your first piece of work"
item = {"id": "first-item", "title": goal[:100], "state": "todo", "next": "claude", "attempts": 0, "updated": None, "notes": ""}
json.dump({"halt": False, "config": {"deadline": None}, "items": [item]}, open(sys.argv[2], "w"), indent=2)
' "$goal" "$desk/STATE.json"
for id in claude codex; do
  cat > "$desk/status/$id.json" <<EOF
{ "agent": "$id", "heartbeat": null, "runStartedAt": null, "runFinishedAt": null,
  "lastResult": "idle", "next": "", "proofToken": null,
  "limits": { "state": "unknown", "checkBackAt": null } }
EOF
done
# Keep the logs out of the history, and start the private git history.
printf '_state/\n.desk-run.lock\n' > "$desk/.gitignore"
(cd "$desk" && git init -q && git add -A . && git -c user.name=local-mode -c user.email=local@desk commit -q -m "start") \
  || { echo "Could not start the git history in $desk. Nothing is switched on. Delete that folder and try again."; exit 1; }
# Make the work-folder branch once, here, so a run can never take over an older branch.
if [ -n "$folder" ]; then
  git -C "$folder" switch -c "desk/$name" >/dev/null 2>&1 \
    || { echo "Could not make branch desk/$name in $folder. Nothing is switched on."
         echo "To try again: delete the folder $desk (only that one; leave $folder alone), then run setup again."; exit 1; }
fi

# --- Make the timers. Each timer is a small text file that tells macOS what to run and when. ---
make_plist() {   # make_plist <job> <when> <command...>   (<when> is "minutes 0 30" or "every 600")
  job=$1; when=$2; shift 2
  plist="$agents/com.localdesk.$name.$job.plist"
  {
    echo '<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict>'
    echo "<key>Label</key><string>com.localdesk.$name.$job</string>"
    echo "<key>ProgramArguments</key><array>"
    for part in "$@"; do echo "<string>$part</string>"; done
    echo "</array>"
    case "$when" in
      minutes*) echo "<key>StartCalendarInterval</key><array>"
                for m in ${when#minutes}; do echo "<dict><key>Minute</key><integer>$m</integer></dict>"; done
                echo "</array>" ;;
      every*)   echo "<key>StartInterval</key><integer>${when#every}</integer>" ;;
      always)   echo "<key>RunAtLoad</key><true/><key>KeepAlive</key><true/>" ;;
    esac
    echo "</dict></plist>"
  } > "$plist"
  launchctl bootout "gui/$uid" "$plist" 2>/dev/null
  launchctl bootstrap "gui/$uid" "$plist" || {
    echo "The $job timer would not start. You are in manual mode for desk '$name'."
    echo "To remove the partial setup: sh setup.sh --uninstall $name"; exit 1; }
}
make_plist claude    "minutes 0 30" /bin/sh "$kit/run-agent.sh" claude "$desk"
make_plist codex     "minutes 15 45" /bin/sh "$kit/run-agent.sh" codex "$desk"
make_plist watchdog  "every 600" /usr/bin/python3 "$kit/watchdog.py" "$desk"
make_plist keepawake always /usr/bin/caffeinate -i -s

echo
echo "Done. Desk '$name' is on. Check BRIEF.md says what you want; if this is your first desk, do the proof of life (guide, section 6: protocols/local-mode.md)."
echo "To remove everything later: sh setup.sh --uninstall $name"
