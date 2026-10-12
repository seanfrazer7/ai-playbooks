#!/usr/bin/env python3
"""watchdog.py DESK [--challenge | --check | --test-alert] [--silent-after MINUTES]

No AI in here. With no option it checks the desk and shows a macOS notification if
something is wrong (a timer runs it every 10 minutes). The options are for the proof of life:
  --challenge   post a secret token for each agent in MESSAGES.md
  --check       did each agent, woken by its own timer, write its token and quote its partner's?
  --test-alert  show a test notification
"""
import json, os, subprocess, sys, time, secrets
from datetime import datetime, timezone

AGENTS = ["claude", "codex"]

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def minutes_ago(iso):
    """How many minutes ago an ISO time was (None if it is empty or unreadable)."""
    try:
        then = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - then).total_seconds() / 60
    except (TypeError, ValueError):
        return None

def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None

def notify(desk, text):
    """Show a notification. The text is passed as an argument, so quotes in it are harmless."""
    script = 'on run argv\ndisplay notification (item 2 of argv) with title (item 1 of argv)\nend run'
    subprocess.run(["osascript", "-e", script, "Desk " + os.path.basename(desk), text])

def problems(desk, silent_after):
    """Return a list of plain-English problems. An empty list means all is well."""
    state = load(desk + "/STATE.json")
    if state is None:
        return ["STATE.json is missing or is not valid JSON (check commas and quotes)."]
    if state.get("halt") or state.get("terminal"):
        return []                                    # halted or finished: stay quiet
    found = []
    for agent in AGENTS:
        s = load("%s/status/%s.json" % (desk, agent)) or {}
        paused = s.get("limits", {}).get("state") == "paused"
        age = minutes_ago(s.get("heartbeat"))
        never = age is None
        if never:                                    # no turn yet: time it from when the desk was made
            try:
                made = os.stat(desk + "/.git").st_birthtime
            except (OSError, AttributeError):
                made = os.path.getctime(desk + "/STATE.json")
            age = (time.time() - made) / 60
        if not paused and age > silent_after:
            found.append("%s has %s for over %d minutes." % (
                agent, "never had a turn" if never else "been silent", silent_after))
        if os.path.exists("%s/_state/%s.failed" % (desk, agent)):
            found.append("%s's last run failed. Read _state/%s.out" % (agent, agent))
    lock = desk + "/.desk-run.lock"
    if os.path.isdir(lock) and time.time() - os.path.getmtime(lock) > 45 * 60:
        found.append("The folder lock has been stuck for over 45 minutes.")
    deadline = minutes_ago(state.get("config", {}).get("deadline"))
    if deadline is not None and deadline > 0:
        found.append("The deadline has passed.")
    return found

def watch(desk, silent_after):
    """Write ALERT.txt, and notify once per problem (again after 6 hours if it is still there)."""
    os.makedirs(desk + "/_state", exist_ok=True)
    found = problems(desk, silent_after)
    seen_file = desk + "/_state/alerted.json"
    seen = load(seen_file) or {}
    for text in found:
        if time.time() - seen.get(text, 0) > 6 * 3600:
            notify(desk, text)
            seen[text] = time.time()
    seen = {t: when for t, when in seen.items() if t in found}      # forget problems that are fixed
    with open(seen_file, "w") as f:
        json.dump(seen, f)
    alert = desk + "/_state/ALERT.txt"
    if found:
        with open(alert, "w") as f:
            f.write(now() + "\n" + "\n".join(found) + "\n")
    elif os.path.exists(alert):
        os.remove(alert)
    print("\n".join(found) or "All quiet.")

def challenge(desk):
    """Post one secret token per agent. Only an agent that really woke up can copy its own."""
    tokens = {a: secrets.token_hex(4) for a in AGENTS}
    with open(desk + "/_state/challenge.json", "w") as f:
        json.dump({"time": now(), "tokens": tokens}, f)
    with open(desk + "/MESSAGES.md", "a") as f:
        f.write("\n### Human → all · PROOF OF LIFE\nTokens: claude = %s, codex = %s\n" % (tokens["claude"], tokens["codex"]))
    print("Challenge posted at %s. Close both apps, then wait about 45 minutes and run --check." % now())

def check(desk):
    """Each agent must have its own token in its own status file, and quote the partner's token."""
    c = load(desk + "/_state/challenge.json")
    if not c:
        sys.exit("Run --challenge first.")
    messages = open(desk + "/MESSAGES.md").read()
    passed = {}
    for agent, partner in (("claude", "codex"), ("codex", "claude")):
        s = load("%s/status/%s.json" % (desk, agent)) or {}
        mine = s.get("proofToken") == c["tokens"][agent]
        fresh = (s.get("heartbeat") or "") > c["time"]            # ISO times compare as text
        replies = [m for m in messages.split("### ")
                   if m.startswith(agent + " →") and "PROOF" in m.split("\n")[0] and c["tokens"][partner] in m]
        passed[agent] = mine and fresh and bool(replies)
        print("%-7s own token: %-3s  heartbeat after challenge: %-3s  quoted %s's token: %s" % (
            agent, "yes" if mine else "NO", "yes" if fresh else "NO", partner, "yes" if replies else "NO"))
    if all(passed.values()):
        print("\nMODE: HANDS-OFF. Both agents woke up on their own and talked to each other.")
    elif passed["claude"]:
        print("\nMODE: CLAUDE-ONLY. Claude works alone; you review its work by hand (or paste your partner's reply yourself).")
    else:
        print("\nMODE: NOT WORKING. Claude did not wake up. Read _state/claude.log and _state/claude.out.")

if __name__ == "__main__":
    args = sys.argv[1:]
    silent = 150                                                  # minutes; the timers run every 30
    if "--silent-after" in args:
        i = args.index("--silent-after")
        silent = int(args[i + 1])
        del args[i:i + 2]
    if not args or not os.path.isdir(args[0]):
        sys.exit(__doc__)
    desk, option = args[0].rstrip("/"), (args[1] if len(args) > 1 else "")
    if option == "--challenge":
        challenge(desk)
    elif option == "--check":
        check(desk)
    elif option == "--test-alert":
        notify(desk, "Test alert. If you can read this, alerts work.")
    else:
        watch(desk, silent)
