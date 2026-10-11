#!/usr/bin/env python3
"""Lists the desks in this repo for the workflows. Standard library only.

  desks.py all                         every desk folder (for the watchdog), one name per line
  desks.py wake --agent claude [--only NAME] [--changed FILE]
                                       JSON list of desks this agent's workflow should run now

A desk is a folder desks/<name>/ with a STATE.json. Folders starting with "_" are templates.
A desk is active unless STATE.json says "halt": true or "terminal": "complete".
"""

import json
import os
import sys

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

    out = []
    for name in desk_names():
        if only and name != only:
            continue
        if changed is not None and name not in changed:
            continue
        state = load_state(name)
        if not is_active(state):
            continue
        info = (state.get("agents") or {}).get(agent) or {}
        if info.get("wakeWorkflow") != workflow:
            continue
        app = state.get("appRepo")
        app = app if isinstance(app, str) and "/" in app and "<" not in app else ""
        out.append({"desk": name, "appRepo": app, "appBranch": state.get("appBranch") or ""})
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
