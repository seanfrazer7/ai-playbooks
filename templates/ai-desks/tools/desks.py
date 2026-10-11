#!/usr/bin/env python3
"""Lists the desks in this repo for the workflows. Standard library only.

  desks.py all                         every desk folder (for the watchdog), one name per line
  desks.py wake --agent claude [--only NAME] [--changed FILE]
                                       JSON list of desks this agent's workflow should run now

With --changed, a desk is picked if a file other than a status file changed in it, or if the
agent is due anyway (see due_reason). Pass an empty file to pick only desks where it's due.
That makes every partner heartbeat a clock: it wakes Claude only when Claude is needed.

A desk is a folder desks/<name>/ with a STATE.json. Folders starting with "_" are templates.
A desk is active unless STATE.json says "halt": true or "terminal": "complete".
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = "desks"
WORKFLOW = {"claude": "claude-wake.yml"}


def desk_names():
    if not os.path.isdir(ROOT):
        return []
    return sorted(n for n in os.listdir(ROOT)
                  if not n.startswith(("_", ".")) and os.path.isfile(os.path.join(ROOT, n, "STATE.json")))


def load_state(name):
    try:
        with open(os.path.join(ROOT, name, "STATE.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def is_active(state):
    return bool(state) and not state.get("halt") and state.get("terminal") != "complete"


def parse_time(value):
    if not value or not isinstance(value, str):
        return None
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def due_reason(name, state, agent, now):
    """Why the agent should run now even though nothing new arrived, or None."""
    cfg = state.get("config") or {}
    try:
        with open(os.path.join(ROOT, name, "status", f"{agent}.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        return "it has no readable status file yet"
    times = [t for t in (parse_time(st.get("heartbeat")), parse_time(st.get("runFinishedAt"))) if t]
    last = max(times) if times else None
    limits = st.get("limits") or {}
    back = parse_time(limits.get("checkBackAt"))
    if limits.get("state") == "paused" and back:
        if now < back:
            return None
        if not last or last < back:
            return "its usage pause is over"
    if not last:
        return "it has never run"
    idle = now - last
    owns = any(i.get("next") == agent and i.get("state") not in ("done", "parked")
               for i in state.get("items") or [])
    if owns and idle >= timedelta(minutes=cfg.get("workWaitingMin", 25)):
        return f"work is waiting for it and it last ran {int(idle.total_seconds() // 60)} min ago"
    if idle >= timedelta(minutes=cfg.get("checkInMin", 60)):
        return f"it hasn't checked in for {int(idle.total_seconds() // 60)} min"
    return None


def changed_desks(path):
    """Desks with a changed file that isn't only an agent heartbeat or the status page."""
    names = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("/")
            if len(parts) >= 3 and parts[0] == ROOT and parts[2] not in ("status", "STATUS.md"):
                names.add(parts[1])
    return names


def main(argv):
    if not argv or argv[0] not in ("all", "wake"):
        sys.exit(__doc__)
    if argv[0] == "all":
        print("\n".join(desk_names()))
        return 0

    agent, only, changed = "claude", None, None
    args = iter(argv[1:])
    for a in args:
        if a == "--agent":
            agent = next(args)
        elif a == "--only":
            only = next(args) or None
        elif a == "--changed":
            changed = changed_desks(next(args))
    workflow = WORKFLOW.get(agent, f"{agent}-wake.yml")
    now = parse_time(os.environ.get("DESKS_NOW")) or datetime.now(timezone.utc)

    out = []
    for name in desk_names():
        if only and name != only:
            continue
        state = load_state(name)
        if not is_active(state):
            continue
        info = (state.get("agents") or {}).get(agent) or {}
        if info.get("wakeWorkflow") != workflow:
            continue
        if changed is not None:
            if name in changed:
                print(f"{name}: new messages or work", file=sys.stderr)
            else:
                reason = due_reason(name, state, agent, now)
                if not reason:
                    print(f"{name}: nothing new and {agent} isn't due", file=sys.stderr)
                    continue
                print(f"{name}: {agent} is due because {reason}", file=sys.stderr)
        app = state.get("appRepo")
        app = app if isinstance(app, str) and "/" in app and "<" not in app else ""
        out.append({"desk": name, "appRepo": app, "appBranch": state.get("appBranch") or ""})
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
