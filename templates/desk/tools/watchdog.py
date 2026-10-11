#!/usr/bin/env python3
"""Desk watchdog: checks a two-agent desk for stuck or silent agents.

Uses no AI and only the Python standard library. Reads STATE.json and
status/<id>.json, writes a Markdown report, and exits with:
  0  all clear
  1  something needs attention (see the report)
  3  the run is finished or halted (the workflow switches itself off)

Usage: python3 watchdog.py [desk_dir] [--out alerts.md] [--wake-out wake.txt]
Set WATCHDOG_NOW=2026-10-10T07:30:00Z to test against a fixed time.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

OPEN_STATES_EXCLUDED = {"done", "parked"}
DEFAULTS = {
    "silentAfterMin": 90,
    "itemStallMin": 180,
    "unfinishedRunMin": 60,
    "maxAttempts": 3,
    "maxBounces": 4,
    "sharedPool": False,
    "deadline": None,
    "budget": {},
}
PAUSE_GRACE = timedelta(minutes=15)


def parse_time(value):
    """Parse an ISO time. Times without a zone are treated as UTC."""
    if not value or not isinstance(value, str):
        return None
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def fmt(t):
    return t.strftime("%Y-%m-%d %H:%M UTC") if t else "never"


def ago(now, t):
    if not t:
        return "never"
    mins = max(0, int((now - t).total_seconds() // 60))
    return f"{mins // 60}h {mins % 60:02d}m ago" if mins >= 60 else f"{mins}m ago"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Report:
    def __init__(self):
        self.alerts = []  # (key, text): key is stable so repeats don't re-notify
        self.notes = []
        self.wake = []

    def alert(self, key, text):
        self.alerts.append((key, text))

    def fingerprint(self):
        keys = "\n".join(sorted(k for k, _ in self.alerts))
        return hashlib.sha256(keys.encode()).hexdigest()[:12] if keys else ""


def check(desk, now):
    r = Report()
    try:
        state = load_json(os.path.join(desk, "STATE.json"))
    except (OSError, ValueError) as e:
        r.alert("state-invalid", f"`STATE.json` can't be read: {e}. Both agents may be stuck on it.")
        return r, None, {}

    if state.get("halt"):
        r.notes.append("The run is halted (`halt: true`).")
        return r, "finished", {}
    if state.get("terminal") == "complete":
        r.notes.append("The run is complete (`terminal: complete`).")
        return r, "finished", {}

    cfg = dict(DEFAULTS)
    cfg.update(state.get("config") or {})
    agents = state.get("agents") or {}
    items = state.get("items") or []
    open_items = [i for i in items if i.get("state") not in OPEN_STATES_EXCLUDED]
    silent_after = timedelta(minutes=cfg["silentAfterMin"])

    deadline = parse_time(cfg.get("deadline"))
    if deadline and now > deadline:
        r.alert("deadline", f"The deadline ({fmt(deadline)}) has passed and the run isn't confirmed complete.")

    statuses, paused, quiet = {}, set(), []
    for aid, info in agents.items():
        path = os.path.join(desk, "status", f"{aid}.json")
        try:
            st = load_json(path)
        except OSError:
            r.alert(f"{aid}:no-status", f"**{aid}** has no `status/{aid}.json`. It may never have joined.")
            continue
        except ValueError as e:
            r.alert(f"{aid}:status-invalid", f"`status/{aid}.json` isn't valid JSON: {e}.")
            continue
        statuses[aid] = st
        hb = parse_time(st.get("heartbeat"))
        limits = st.get("limits") or {}
        cba = parse_time(limits.get("checkBackAt"))
        overdue = False

        if limits.get("state") == "out":
            r.alert(f"{aid}:out", f"**{aid}** says it's out of usage or credit. Top it up, or replace it (START-HERE C).")
        if limits.get("state") == "paused" and cba:
            if now < cba + PAUSE_GRACE:
                paused.add(aid)
                r.notes.append(f"{aid} is paused for its usage limit until {fmt(cba)}.")
            elif not hb or hb < cba:
                r.alert(f"{aid}:no-return", f"**{aid}** was due back from its usage pause at {fmt(cba)}, "
                        f"but its last heartbeat is {ago(now, hb)}.")
                overdue = True
        elif not hb:
            r.alert(f"{aid}:never", f"**{aid}** has never written a heartbeat. Its schedule may not be set up.")
            overdue = True
        elif now - hb > silent_after:
            r.alert(f"{aid}:silent", f"**{aid}** has been silent since {fmt(hb)} ({ago(now, hb)}) "
                    "with no pause note. It may have run out of usage or lost its schedule.")
            overdue = True
            quiet.append(aid)

        started, finished = parse_time(st.get("runStartedAt")), parse_time(st.get("runFinishedAt"))
        if started and (not finished or finished < started):
            if now - started > timedelta(minutes=cfg["unfinishedRunMin"]):
                r.alert(f"{aid}:unfinished", f"**{aid}**'s run {st.get('run', '?')} started {ago(now, started)} "
                        "and never finished. It probably crashed or ran out mid-run.")

        max_runs = (cfg.get("budget") or {}).get("maxRunsPerAgent")
        if max_runs and isinstance(st.get("run"), int) and st["run"] >= max_runs:
            r.alert(f"{aid}:budget", f"**{aid}** has used its run budget ({st['run']} of {max_runs}).")

        if overdue and info.get("wakeWorkflow"):
            r.wake.append(info["wakeWorkflow"])

    if cfg.get("sharedPool") and agents and len(quiet) == len(agents):
        r.notes.append("Both agents share one usage pool and both are quiet, so this is probably a usage reset. "
                       "They should come back on their own after it.")

    for item in open_items:
        iid, nxt = item.get("id", "?"), item.get("next")
        updated = parse_time(item.get("updated"))
        if item.get("state") == "blocked" or nxt == "human":
            r.alert(f"item:{iid}:human", f"Item `{iid}` is waiting for you: {item.get('notes') or item.get('title', '')}")
            continue
        if nxt not in agents:
            r.alert(f"item:{iid}:no-owner", f"Item `{iid}` has no valid `next` agent ({nxt!r}). Nobody will pick it up.")
            continue
        if updated and now - updated > timedelta(minutes=cfg["itemStallMin"]) and nxt not in paused:
            r.alert(f"item:{iid}:stalled", f"Item `{iid}` has waited on **{nxt}** since {fmt(updated)} ({ago(now, updated)}).")
        if (item.get("attempts") or 0) >= cfg["maxAttempts"]:
            r.alert(f"item:{iid}:attempts", f"Item `{iid}` has reached {item['attempts']} attempts and isn't parked (rule S4).")
        if (item.get("bounces") or 0) >= cfg["maxBounces"]:
            r.alert(f"item:{iid}:bounces", f"Item `{iid}` has bounced between the agents {item['bounces']} times (rule S6).")

    if not open_items and state.get("terminal") != "complete":
        r.notes.append("No open items are left; waiting for the finish handshake.")

    return r, None, statuses


def render(r, now, statuses, finished):
    lines = [f"## Desk watchdog · {fmt(now)}", ""]
    if finished:
        lines.append("The run is finished or halted. The watchdog is switching itself off.")
    elif r.alerts:
        lines.append(f"**{len(r.alerts)} thing(s) need attention:**")
        lines.append("")
        lines += [f"- {text}" for _, text in r.alerts]
    else:
        lines.append("All clear.")
    if r.notes:
        lines += ["", "Notes:"] + [f"- {n}" for n in r.notes]
    if statuses:
        lines += ["", "| Agent | Last heartbeat | Last result | Usage | Next |", "|---|---|---|---|---|"]
        for aid, st in statuses.items():
            lim = st.get("limits") or {}
            usage = lim.get("state", "?")
            if lim.get("checkBackAt"):
                usage += f" (back {lim['checkBackAt']})"
            nxt = str(st.get("next", "")).replace("|", "/")[:80]
            lines.append(f"| {aid} | {ago(now, parse_time(st.get('heartbeat')))} | "
                         f"{st.get('lastResult', '')} | {usage} | {nxt} |")
    if r.wake:
        lines += ["", "Re-running wake workflows: " + ", ".join(f"`{w}`" for w in r.wake)]
    lines += ["", f"<!-- fp:{r.fingerprint()} -->"]
    return "\n".join(lines) + "\n"


def main(argv):
    desk, out, wake_out = ".", None, None
    args = iter(argv)
    for a in args:
        if a == "--out":
            out = next(args)
        elif a == "--wake-out":
            wake_out = next(args)
        else:
            desk = a
    now = parse_time(os.environ.get("WATCHDOG_NOW")) or datetime.now(timezone.utc)

    r, finished, statuses = check(desk, now)
    text = render(r, now, statuses, finished)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        with open(out + ".fp", "w", encoding="utf-8") as f:
            f.write(r.fingerprint())
    if wake_out:
        with open(wake_out, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(set(r.wake))))
    sys.stdout.write(text)
    if finished:
        return 3
    return 1 if r.alerts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
