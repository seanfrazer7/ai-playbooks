---
name: overnight-handoff
description: Set up an overnight Claude Code + ChatGPT run (art mode or design-debate mode). Creates the shared desk repo, BRIEF.md and STATE.json, writes the ChatGPT prompt, and runs the bedtime checklist. Refuses to say goodnight until a wake-up has actually fired. Use when the user says they want work to continue overnight or while they're away with ChatGPT helping.
---

# Overnight handoff

You are setting up an overnight run in which you (Claude Code) are the **builder**, ChatGPT is the **artist** (art mode) or **critic** (design-debate mode), and the human is asleep. Follow `protocols/overnight-claude-chatgpt.md` from the ai-playbooks repo. If it isn't available, these steps are the minimum.

The biggest risk is **not** the work itself. It's that you silently stop waking up. The first real run lost 7 hours that way. Everything below exists to prevent that.

## 1. Brief (while the human is still here)

1. Ask which mode (art or design-debate), what the project is, and what "done" looks like.
2. Ask **up to 3** questions about decisions you'd otherwise have to guess.
3. Ask what you may decide alone. Default: anything on a branch that doesn't touch production data, money, publishing or other people.
4. Write `BRIEF.md` with the answers.

## 2. Desk repo

1. Create a **private** repo `<owner>/<project>-desk` with `gh repo create --private`. Never make it public; it will hold the conversation and the work in progress.
2. Add these files:
   - `PROTOCOL.md`: a copy of the protocol.
   - `BRIEF.md`
   - `STATE.json`: every item, `phase`, `terminal: null`, and `heartbeats`.
   - `MESSAGES.md`
   - `GPT-LOG.md`
   - `incoming/` (art mode) or `DECISION.md` (debate mode, filled in later).
   - `references/` if a character or style must stay consistent.
3. Art mode: write `ART-QUEUE.md` with exact sizes, transparency, protected pixel regions as numbers, one shared style block, and one prompt per image.
4. Give the human the matching ChatGPT prompt from `prompts/`, filled in. Tell them:
   - Use **Agent mode + the GitHub connector** (never the website).
   - Grant the connector access to the desk repo.
   - Schedule the chat at :00 and :30.

## 3. Your wake-up: it must survive this chat session

Pick the most durable option available, in this order:

1. **A GitHub Action on the desk repo** that runs Claude Code on every push (and on a :15/:45 schedule). It needs an `ANTHROPIC_API_KEY` secret, which the human adds.
2. **Durable scheduled tasks** in the Claude app, if available.
3. Only as a backup on top of one of the above: an in-session watcher (`Monitor`, re-armed every time it expires). **Never rely on session-only timers alone.** They didn't fire overnight on the first run.

Never turn off a wake-up that is working. Only add backups.

## 4. Bedtime checklist: don't say goodnight until every box is ticked

- [ ] `BRIEF.md` is answered, and the limits are written down.
- [ ] `STATE.json` lists every item.
- [ ] **Your wake-up has fired once for real.** Trigger it, have it append `heartbeat OK <time>` to `MESSAGES.md`, and show the human that line.
- [ ] ChatGPT has done one run and written its heartbeat.
- [ ] Work happens on a branch, and you've confirmed that branch won't deploy or cost money.
- [ ] If the wake-up runs on this computer: it's plugged in and kept awake.

If any box can't be ticked, tell the human plainly which one and what that means ("If my trigger doesn't fire, nothing will happen until you wake up"). Then let them decide.

## 5. Each time you wake

1. Update your heartbeat in `STATE.json`.
2. Pull the desk repo and read new messages and `STATE.json`.
3. Do the work that's waiting on you. Art mode: process new images, integrate them, test them, commit to the branch, mark them `integrated`, and reply. Debate mode: take your turn in the current round.
4. If ChatGPT's heartbeat is more than 90 minutes old while work is open, post `⚠️ ChatGPT silent since <time>` and keep going on everything you can.
5. Stay quiet when nothing has changed.

## 6. Finish

1. When everything is integrated, built and tested: post `FINAL INTEGRATION COMPLETE` with the commit, and set `terminal: "claude-done"`.
2. Keep waking until ChatGPT posts `CONFIRMED COMPLETE`.
3. Write `MORNING.md`:
   - what got done, with commits
   - what didn't, and why
   - decisions waiting on the human
   - how to try it
   - the exact words to ship it
4. Never merge, publish or deploy. That's the human's call.
