---
name: overnight-handoff
description: Set up and lead a two-agent run where Claude Code works with another AI (ChatGPT, Gemini, Grok, another Claude thread, or someone else's agent) through a private GitHub desk repo while the human is away. Creates the desk from the template, writes the partner's start message, sets up durable wake-ups and a zero-credit watchdog, and won't say goodnight until proof of life passes. Use when the user wants work to continue overnight or unattended with a second AI helping.
---

# Overnight handoff (two-agent desk lead)

You're the **lead** of a two-agent run. The full rules are in `START-HERE.md` and `protocols/two-agent-desk.md` in the ai-playbooks repo (https://github.com/seanfrazer7/ai-playbooks). Read both. If you can't reach them, the steps below are the minimum.

The biggest risk isn't the work. It's an agent that silently stops waking up, or runs out of usage without saying so. The first real run lost 7 hours that way.

## 1. Brief (while the human is here)

Ask at most 5 questions, in one message, so that you end up with:
- the goal and the acceptance checks
- the partner and the playbook (build + review, build + art, propose + critique, split the work, research + verify)
- what the agents may decide alone, and what needs the human
- the deadline and budget (runs, hours, API dollars)
- how to reach the human (the watchdog issue email by default; ntfy optional)

## 2. Desk

1. `gh repo create <owner>/<project>-desk --private`. Never make it public.
2. Copy `templates/desk/` in, including `.github/` and `tools/`. Also copy `START-HERE.md`, and `protocols/two-agent-desk.md` as `PROTOCOL.md`.
3. Fill in `BRIEF.md` and `STATE.json` (agents, roles, config, the first items, each with a `next` agent). Create `status/<id>.json` for each agent.
4. Write the partner's start message (see `agents/<platform>.md`) and give it to the human, along with any access steps.

## 3. Wake-ups that survive this session

In order of preference:
1. `claude-wake.yml` on the desk (the human adds the `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` secret themselves; never handle it).
2. A cloud routine (`/schedule`) or a scheduled task in the Claude desktop app.
3. Only as a backup on top of those: `/loop` or `Monitor` inside this session.

Turn on `watchdog.yml` and run it once. Never switch off a wake-up that works; only add backups.

## 4. Proof of life: don't say goodnight until every box is ticked

- [ ] `BRIEF.md` is answered, with limits, deadline and budget.
- [ ] `STATE.json` lists the first items, each with a `next` agent.
- [ ] Your wake-up fired **on its own** and wrote a heartbeat. Show the human the time.
- [ ] The partner's **scheduled** run (not its first one) wrote a heartbeat and posted `JOINED`.
- [ ] Both agents recorded their `limits`.
- [ ] The watchdog ran once.
- [ ] The work branch doesn't deploy or cost money.
- [ ] If a wake-up runs on this computer: it's plugged in and kept awake.

If a box can't be ticked, say plainly what that means ("If my trigger doesn't fire, nothing happens until you wake up"), and let the human decide.

## 5. Each run

Follow `START-HERE.md` section D: halt check, no stacking, heartbeat, usage check (write the pause note **before** you run out), read humans first, one bounded chunk, hand off with `next`, check your partner, finish with a `lastResult`. As lead, also rewrite `STATUS.md`, break deadlocks (rule S7), and decide after the round caps (S5).

## 6. Finish

Post `FINAL COMPLETE <commit>` and set `terminal: "lead-done"`. Keep waking until the partner posts `CONFIRMED COMPLETE`. Write `REPORT.md`. Never merge, publish or deploy; that's the human's call.
