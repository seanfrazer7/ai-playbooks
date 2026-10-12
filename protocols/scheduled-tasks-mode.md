# Scheduled-tasks mode: Claude and ChatGPT apps, one folder, no Terminal

Claude and ChatGPT take turns on a shared folder using **each desktop app's own scheduled tasks**. Nothing to install: no Terminal, no timers of your own, no GitHub. Each turn is a one-time scheduled task at a set time, and the agents leave notes for each other in one append-only file.

> **Tested once (Oct 12, 2026)** on a managed work Mac (macOS 27.0.1) with the Claude desktop app and the ChatGPT desktop app (local mode). There were two four-turn exercises, about 7 hours of testing:
> - Each turn **ran unattended** once it was set up correctly. Reviews were real: one caught a flaw in a draft, and a final check returned an honest **NOT DONE** rather than rubber-stamping.
> - **It isn't fully hands-off yet.** One turn never ran (cause unconfirmed), and one Claude turn stalled silently for 30+ minutes. Both needed a person to notice and re-time the remaining turns. See [Pitfalls](#pitfalls).
>
> **Experimental, personal use.** Both apps send what they read to Anthropic or OpenAI. See [Suitable use and data](two-agent-desk.md#suitable-use-and-data).

**When to use which:**
- **This mode:** you can't or don't want to use Terminal, and a few planned turns are enough.
- [**Local mode**](local-mode.md) (Claude Code + Codex with Terminal): repeating timers, a lock, a watchdog and a stricter proof of life.
- [**ask-gpt**](../skills/ask-gpt/SKILL.md): you're at the computer and just want a second opinion now.

## What you need
- The **Claude desktop app** (paid plan) with scheduled tasks, and the **ChatGPT desktop app** with scheduled tasks in local mode.
- A Mac that stays **awake and plugged in, with both apps open**. Both vendors say tasks only fire while the app runs **[verify]** (sleep wasn't tested).
- One new folder for the desk, set up as a **saved project in ChatGPT** (see pitfall 3).

## The desk
In the folder:
- `BRIEF.md`: the goal, who does what, the turn plan, and the rules below
- `MESSAGES.md`: append only; every turn adds exactly one entry
- `work/`: the drafts and results

## Rules for every turn
Put these in **every** task's instructions, with the folder's full path:

1. Read `BRIEF.md` and `MESSAGES.md` first. If any entry says HALT, stop and change nothing. HALT is final.
2. Act only if the **last** entry hands off to you for your step. If not, add exactly one "skipped" entry and stop. (In testing, this guard held every time a turn ran out of order.)
3. Re-read the files right before writing. Never edit or delete another agent's entries.
4. Touch only files inside the desk folder.
5. Add exactly one entry per turn, naming the next agent, the action requested, and the time.
6. **Claude: use only file read, write and edit tools, no shell.** A turn that used a shell command stalled (pitfall 6).

## The turn plan
Five one-time turns, 15 minutes or more apart:

| Turn | Who | What |
|---|---|---|
| 1 | Claude | Draft |
| 2 | ChatGPT | Review: specific fixes |
| 3 | Claude | Apply the fixes |
| 4 | ChatGPT | Final check: DONE or NOT DONE, with gaps |
| 5 | Claude | If NOT DONE, fix the gaps and write what's still open |

The tested plan had four turns. After the final check said NOT DONE, nobody re-checked, so the fifth turn is added here.

**Create every task before turn 1 fires.** A chain of one-time tasks can't wait for you (pitfall 4).

## Setting up the ChatGPT turns
Open a **new** ChatGPT thread with the saved project selected, and send this, filled in:

```text
Create TWO separate one-time scheduled tasks, both local mode, both in the saved project <PROJECT NAME>. Task A runs once today at <TIME A>. Task B runs once today at <TIME B>. Use a one-occurrence rule with no DTSTART and no timezone text, for example FREQ=DAILY;COUNT=1;BYHOUR=<h>;BYMINUTE=<m>. Do NOT use suggested_create or any proposal mode. If either is rejected, STOP and paste me the exact error. No workarounds, no web search. Create A first, then B.

SHARED RULES (put in each task's own instructions): <the rules above, with the full folder path>

TASK A, <STEP>: <what to do and what to append>
TASK B, <STEP>: <what to do and what to append>

Right now only create the two tasks; edit no file. Then open the Scheduled page and reply with two lines, one per task: Active or proposal only; exact next-run time; local or cloud; project bound to. Never say a task is scheduled unless the Scheduled page shows it Active with a next-run time.
```

**Then look at ChatGPT's Scheduled page yourself.** Each task should show as **Active** with a next-run time.

## Setting up the Claude turns
In the Claude desktop app, create a **one-time scheduled task** at a fixed date and time for each Claude turn. Include the rules and the step's instructions. You can ask Claude to create them. **Then check each one shows as enabled with a next-run time.**

## Pitfalls
Found in testing:

1. **A proposal card isn't an active task.** ChatGPT created a proposal and reported it as "scheduled". Only trust the Scheduled page showing **Active** with a next-run time.
2. **No timezone and no `DTSTART`** in ChatGPT's schedule rule. Both were rejected, for example: `active task creation cannot include a timezone-anchored start time`. Give a bare local clock time.
3. **Make the folder a saved ChatGPT project first.** A task bound to a new folder failed with just `Failed to create automation.` (most likely because it wasn't a saved project). If you can't register a new project, put the desk inside an existing saved project. Its boundary is then the whole parent folder, and "stay in this subfolder" is only an instruction.
4. **Create all the tasks up front.** A missing task means a missed turn. Turns that are missed or skipped don't come back by themselves.
5. **An agent's note isn't proof of what started it.** A line saying "started by the scheduler" was written during a manual request. Check each app's run history.
6. **A Claude turn that ran a shell command stalled** for 30+ minutes with no alert, most likely waiting for an approval. A later turn told to use file tools only finished cleanly. That's one data point, but prefer file tools.
7. **A stall uses up the turns after it.** The next turns correctly logged "skipped", and then nothing resumed. Someone has to notice and re-time them.
8. **Keep the Mac awake and plugged in, and both apps open.**
9. **Plan a re-check.** A final NOT DONE means more work; that's turn 5 in the plan above.
10. **Watch for stray edits** when the project is bound to a larger folder: list the files before the run and compare afterwards.

## Checking how it went
- Read `MESSAGES.md` from the top. Each turn should have exactly one entry.
- Compare against each app's **run history**: did every task actually run, and when?
- A turn stuck as "running" for over 25 minutes is a stall. Stop it, add a labelled note to `MESSAGES.md` (for example `### Human → all · correction: <what happened, who's next>`), and create new one-time tasks for the remaining turns.

## Idea, untested: a supervisor task
For an unattended window, add one more Claude scheduled task that does the checking for you: read `MESSAGES.md` and the run histories, spot a stalled or overdue turn, stop a stuck Claude run, add a labelled correction, create replacement one-time Claude tasks, and write a morning summary. Its limits:
- It can't see or re-arm ChatGPT's tasks, so create ChatGPT retry tasks up front.
- It can stall itself, so give it file and scheduler tools only, and approve them once by hand beforehand.
- It needs a repair limit, and must stop at DONE or HALT.

Prove it on a harmless goal first.
