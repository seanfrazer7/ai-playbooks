---
name: local-desk
description: Run a local two-agent desk where Claude Code and Codex take turns on a goal on this Mac, with no GitHub. Use when the user gives a goal for Claude and Codex (or "GPT") to work on together locally, or asks for a desk's status, to check it, or to stop it. Handles first-time setup on this Mac, the proof of life, and watching the desk so the user is told when it's done or stuck.
argument-hint: <goal> [work folder: <path>] | status | stop <name>
---

# Local desk

You help the human run a desk from the [local mode guide](https://github.com/seanfrazer7/ai-playbooks/blob/main/protocols/local-mode.md): Claude Code and Codex take turns on a shared folder in `~/Desks/<name>/`, each woken by a macOS timer. **You are the helper, not one of the desk's agents.**

## Rules
- **Never run the desk's agents yourself** (no `claude -p` or `codex exec` on a desk). The timers must do it, or the proof of life means nothing.
- **Never handle credentials.** The human runs `claude setup-token`, the Keychain command, and the Codex sign-in. Never print the Keychain token (no `-w` output in your replies).
- **Change desks only through the kit's `setup.sh`.** Don't hand-edit `STATE.json`, `MESSAGES.md` or status files.
- The human typing `/local-desk <goal>` is their yes to create that desk, so `setup.sh --yes` is allowed. Anything else that installs, uninstalls or deletes needs a clear yes in chat.
- Give times in the human's local time (check `date`).
- Personal, non-confidential work only. If the goal or folder looks like company code, customer data or anything confidential, stop and ask.

## 1. Work out what was asked
- `status` (or no arguments): go to section 6.
- `stop <name>`: go to section 7.
- Anything else is a goal. Pull out an optional work folder (a path after "work folder:", "in", or similar). If you're unsure what "done" looks like, ask one short question; otherwise go ahead.

## 2. First-time check (every run; it's quick)
Check, in order, and fix only what's missing:
1. **Tools:** `python3`, `git`, `claude`, `codex` exist, and `which claude codex` points into `~/.local/bin`, `/opt/homebrew/bin` or `/usr/local/bin` (the timers only look there). If a tool is elsewhere, tell the human; the fix is the `PATH=` line in `~/DeskKit/run-agent.sh`.
2. **Kit:** if `~/DeskKit/setup.sh` is missing, get it: `git clone --depth 1 https://github.com/seanfrazer7/ai-playbooks ~/Downloads/ai-playbooks` (or `git -C ~/Downloads/ai-playbooks pull` if that folder exists), and use `~/Downloads/ai-playbooks/templates/local-desk/setup.sh` in section 3. It copies itself to `~/DeskKit`.
3. **Codex sign-in:** `codex login status`. If it isn't signed in, ask the human to run `codex` in the Terminal app, choose "Sign in with ChatGPT", then quit it. Wait until they say done, then check again.
4. **Claude token:** `security find-generic-password -s claude-desk-token >/dev/null 2>&1 && echo yes`. If it's missing, the timers can't log Claude in, so ask the human to run, in the Terminal app:
   - `claude setup-token` (approve in the browser, then copy the `sk-ant-oat…` token it prints)
   - `security add-generic-password -a "$USER" -s claude-desk-token -w` (paste it twice; nothing shows), then ⌘K to clear the screen

   Then check it exists again.
5. **Safety, the first time only** (when `~/DeskKit` didn't exist yet): in two lines, remind them it's for personal, non-confidential work, that the Mac must stay awake and plugged in, and that it installs four timers. Ask "OK to install?" and wait for yes.

## 3. Create the desk
Pick a short name from the goal (lowercase letters, digits and dashes; make sure `~/Desks/<name>` doesn't exist). Then run:

`sh ~/DeskKit/setup.sh --yes --name <name> --goal "<the goal, in the human's words>"`, plus `--folder "<path>"` if they gave a work folder (it must be a git project with no uncommitted changes; setup checks this).

If it prints an error, tell the human what it says and stop. Don't work around it.

## 4. First desk on this Mac: proof of life
If `~/DeskKit/.proven` doesn't exist:
1. `cd ~/DeskKit && python3 watchdog.py ~/Desks/<name> --test-alert`, then ask whether a notification appeared. If not: Focus mode, or System Settings → Notifications.
2. `python3 watchdog.py ~/Desks/<name> --challenge`.
3. Tell the human: quit the Claude Code and Codex apps (this chat can stay), keep the Mac plugged in with the lid open, and come back in about 45 minutes.
4. Start a background command (`run_in_background`) that waits until both agents have had a turn after the challenge (both `~/Desks/<name>/_state/claude.log` and `codex.log` have a line after the challenge time, or 60 minutes pass), then runs `python3 ~/DeskKit/watchdog.py ~/Desks/<name> --check` and prints the last lines of both logs.
5. When it finishes: **HANDS-OFF**, so `touch ~/DeskKit/.proven` and tell them it works. **CLAUDE-ONLY** or **NOT WORKING**, so read `_state/<agent>.out` and explain the cause in plain words. "OAuth session expired" means the Claude token step was skipped (section 2.4).

Before the first check, "NOT WORKING" only means no turns have happened yet.

## 5. Watch and tell the human
After creating a desk (and after a passed proof of life), start a background command that checks every 60 seconds and stops when any of these happen:
- every item in `STATE.json` is `done` or `parked`, or an item is `blocked` or has `"next": "human"`
- `_state/ALERT.txt` appears or changes
- `STATE.json` has `"halt": true`
- 12 hours pass

Then tell the human in three lines or fewer: what happened, where the result is (`~/Desks/<name>/work/`), and what they need to do, if anything. Use the PushNotification tool too, since they've probably walked away, e.g. "Desk cheatsheet: done, see work/CHEATSHEET.md". Then offer to turn the desk's timers off (section 7), because idle agents still check in hourly.

The watch only lasts while this chat is open; say so once.

## 6. Status
For each folder in `~/Desks/`: the items' `state` and `next`, the last line of each agent's log (with local times), and whether its timers are loaded (`launchctl list | grep com.localdesk.<name>`). One short table.

## 7. Stop
Confirm with the human first. Then run `sh ~/DeskKit/setup.sh --uninstall <name>`. The desk folder and its work stay. Offer to delete the folder only if they ask.
