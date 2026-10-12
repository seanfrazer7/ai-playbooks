# Local mode: Claude Code and Codex on one Mac, no GitHub

Two AI agents take turns on a shared folder (the **desk**) on your Mac. Each one wakes on its own timer, reads what the other wrote, does a bit of work, and leaves a note. Nothing goes through GitHub. The kit is in [`templates/local-desk/`](../templates/local-desk/): three scripts and two text files.

> **Tested once (Oct 2026)** on macOS 27 with Claude Code 2.1.270 and Codex CLI 0.154: the proof of life passed (**HANDS-OFF**), and the agents finished a small task together with nobody at the Mac. Claude drafted a one-page guide, and Codex reviewed it, improved it and marked it done. The test found three bugs, all fixed in this kit ([case study](../case-studies/two-agent-desk-tests.md)). Anything not yet tested is marked **[verify]**.
>
> **Experimental, personal use.** Same limits as the GitHub version: see [Suitable use and data](two-agent-desk.md#suitable-use-and-data).

## 1. What you need

- A Mac. It must stay **awake and plugged in** while the agents work.
- **Claude Code** (a paid Claude plan) and **Codex**, OpenAI's coding agent (a ChatGPT plan), both as command-line tools. The tested setup installed both with npm, using Node from Homebrew (`brew install node`):
  ```bash
  npm install -g @anthropic-ai/claude-code @openai/codex
  ```
  The timers look for the tools in `~/.local/bin`, `/opt/homebrew/bin` and `/usr/local/bin`. If `which claude` or `which codex` shows a different folder (for example, Node installed with nvm), add that folder to the `PATH=` line near the top of `run-agent.sh`.
- Built-in tools: `sh`, Python 3, `git`, `launchd` (macOS timers). No other services, no extra cost.

**The ChatGPT app can't take part on its own.** It can't run on a timer from your Mac. If you only have the ChatGPT app, you'd open it yourself and ask it to read the desk, which isn't hands-off. Codex is what makes this work.

## 2. Work-computer safety (read before installing)

- **Ask first.** Check your employer's AI and data policies, and whether background jobs and these tools are allowed. Both agents send what they read to OpenAI or Anthropic. "It's local" doesn't make it allowed.
- **Keep out of the desk:** company source code, customer or employee data, passwords, API keys, anything under NDA.
- **Grant nothing extra.** Never grant Full Disk Access, Accessibility, Screen Recording or administrator rights. The kit needs none of them.
- **Where the desk lives:** `~/Desks/`. Not iCloud, Dropbox or OneDrive (they sync half-written files), and not Documents or Desktop (macOS keeps asking background jobs for permission there).
- **One work folder at most.** A goal may name one project folder outside the desk (section 5). Use only a folder you're allowed to give AI tools. Never point a personal desk at a work project, or the reverse.
- **Managed Macs** may block timers, forbid the tools or force sleep. If setup fails for one of these reasons, stop.

## 3. Set up (about 20 minutes)

1. **Get the kit.** In Terminal:
   ```bash
   git clone --depth 1 https://github.com/seanfrazer7/ai-playbooks ~/Downloads/ai-playbooks
   ```
2. **Check the tools and log in.** Run `python3 --version`, `git --version`, `claude --version` and `codex --version`. If macOS offers to install developer tools, accept (it's Apple's). Run `codex` once and sign in.
3. **Give Claude a login that won't expire.** A login made by typing `claude` can expire when it isn't used, and then the timer can't start Claude. This happened in our test. So save a long-lived token in your Keychain:
   ```bash
   claude setup-token
   ```
   Approve in the browser, copy the token Terminal prints (`sk-ant-oat…`), then save it. Paste it when asked, twice; nothing shows while you paste:
   ```bash
   security add-generic-password -a "$USER" -s claude-desk-token -w
   ```
   Press ⌘K to clear the screen. The kit reads the token from the Keychain on each run. Don't paste it anywhere else.
4. **Install your first desk:**
   ```bash
   cd ~/Downloads/ai-playbooks/templates/local-desk && sh setup.sh
   ```
   It asks for a name, lists everything it will create, and waits for you to type `yes`. It creates `~/Desks/<name>/`, copies the kit to `~/DeskKit/` (shared by all your desks), and starts four timers.
5. **Write the goal.** Open `~/Desks/<name>/BRIEF.md` and replace the placeholder line. In `STATE.json`, change the `title` of the one item. (For later desks you can skip this; see section 5.)
6. **Run the proof of life** (section 6) before you walk away.

**To stop one desk:** set `"halt": true` in its `STATE.json` (you can undo this), or add `### Human → all · HALT` to `MESSAGES.md` (permanent). **To remove it:** `sh ~/DeskKit/setup.sh --uninstall <name>`. That turns off its timers; delete `~/Desks/<name>` yourself.

## 4. How it runs

- **Timers:** Claude at :00 and :30, Codex at :15 and :45, the watchdog every 10 minutes, and `caffeinate` to keep the Mac awake while it's plugged in. Your Mac's local time.
- **Each turn** (`run-agent.sh`, about 120 lines with plain-English comments):
  1. Stop if the desk is halted, or the agent left a "paused for usage" note that hasn't expired.
  2. Skip unless a desk file changed since the agent's last successful turn, or an hour has passed.
  3. Take the lock, a folder called `.desk-run.lock`. If it's already there, the other agent is working, so try again next tick. A lock older than 30 minutes is treated as abandoned. Turns are capped at 25 minutes.
  4. Start the agent with one instruction: read `PROTOCOL-LITE.md` and do one turn. Claude runs as `claude -p` with file tools only (no shell). Codex runs as `codex exec` in its `workspace-write` sandbox, limited to the desk.
  5. Save the turn as a git commit in the desk folder (local only), then release the lock. A failed turn doesn't count as done, so the next tick retries it.
- **They talk in `MESSAGES.md`** and put their work in `work/`. Nothing pops up when they finish. Read `MESSAGES.md`, or keep a Claude chat open and ask it to watch the desk and tell you.
- **Undo anything:** `cd ~/Desks/<name>`, `git log` to see each turn, and `git checkout <id> -- <file>` to bring a file back.
- **Usage limits:** an agent that's nearly out writes a pause note with a "back at" time, and the kit skips it until then. **[verify]** Neither tool shows scripts a reliable usage meter, so this depends on the agent noticing. A turn that fails on a limit shows up as a "run failed" alert.

## 5. Starting a new goal with one message

After the first desk, open Claude Code and type:

```text
New desk goal: <what "done" looks like>. Work folder: <full path, or none>. Follow ~/DeskKit/NEW-DESK.md.
```

Claude picks a name, runs the installer with your goal, and tells you the desk name. The timers start, and Codex needs no message of its own. **[verify]** This one-message flow wasn't part of the first test.

**A work folder** is a project (a folder with `.git` inside) that the agents may change, such as a code repo. It must have no uncommitted changes. The kit creates a branch `desk/<name>` there, lets both agents write to that folder, and commits each turn to that branch. Nothing is pushed. Look at the branch yourself (`git log desk/<name>`) and merge it if you like. **[verify]** Work folders weren't part of the first test.

## 6. Proof of life (about 45 minutes, before you leave)

Run these from `~/DeskKit`, replacing `NAME` with your desk name.

1. **Alerts:** `python3 watchdog.py ~/Desks/NAME --test-alert`. A notification should appear. If it doesn't, check Focus mode and System Settings → Notifications.
2. **Post the secret codes:** `python3 watchdog.py ~/Desks/NAME --challenge`. This posts a random code for each agent in `MESSAGES.md`.
3. **Quit the Claude and Codex apps, leave the Mac plugged in with the lid open, and walk away** through at least one turn of each timer (about 45 minutes). Don't run either agent yourself: a run you start proves nothing about the timers.
4. **Check:** `python3 watchdog.py ~/Desks/NAME --check`. An agent passes only if it copied **its own** code into **its own** status file, wrote a heartbeat after the challenge, and replied quoting **its partner's** code. The kit never writes the codes, so an agent that merely started can't pass. The last line tells you the mode:
   - **HANDS-OFF:** both passed. You can walk away.
   - **CLAUDE-ONLY:** Codex didn't pass. Read `_state/codex.log` and `_state/codex.out`.
   - **NOT WORKING:** Claude didn't pass. Read `_state/claude.log` and `_state/claude.out`. "OAuth session expired" means step 3 of setup was skipped.

   Checking before both agents have had a turn shows NOT WORKING. Wait for the ticks.
5. **Optional: test the silent alert.** Turn Codex's timer off with `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.localdesk.NAME.codex.plist`, wait 6 minutes, and run `python3 watchdog.py ~/Desks/NAME --silent-after 5`. You should get a "codex is silent" notification. Turn it back on with `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.localdesk.NAME.codex.plist`. **[verify]** Not yet run in a test.

## 7. The watchdog

`watchdog.py` uses no AI. It shows a macOS notification and writes `_state/ALERT.txt` when: an agent hasn't had a turn for over 150 minutes and isn't paused (a brand-new agent is timed from when the desk was created); a turn failed; the lock has been stuck for over 45 minutes; the deadline has passed; or `STATE.json` can't be read. It tells you once per problem, again after 6 hours if it's still there, and stays quiet when the desk is halted. It doesn't tell you when work is *done*; read `MESSAGES.md` for that.

## 8. If something's wrong

| Symptom | Look at |
|---|---|
| Nothing runs | Is the Mac awake and plugged in? `launchctl list \| grep localdesk` |
| Claude fails with "OAuth session expired" | Setup step 3: save a `claude setup-token` token in the Keychain |
| An agent never wakes | `_state/<agent>.log`, then `_state/<agent>.out` |
| "lock busy" forever | `ls -d ~/Desks/NAME/.desk-run.lock`. It clears itself after 30 minutes, or remove it with `rmdir` |
| You changed a file by mistake | `git log` and `git checkout` in the desk folder |
| You want it all off | `sh ~/DeskKit/setup.sh --uninstall NAME` |

## What this version leaves out

It's the lite version: three scripts you can read in a few minutes. A heavier version was designed, with process-ID lock recovery, a fake-agent self-test, hourly snapshots and a manual installer, but it was never tested, so it isn't published. If you need stricter guarantees, start from the GitHub version, which runs on GitHub's servers instead of your Mac.
