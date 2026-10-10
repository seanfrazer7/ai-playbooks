# Claude ⇄ ChatGPT overnight protocol

A reusable playbook for overnight work where Claude Code (builder) and ChatGPT (artist or critic) coordinate through a private GitHub repo while you sleep.

> **Status (Oct 2026):**
> - **Art mode** ran once for real. The art finished 20/20 and the code was complete, but the builder's wake-up failed, so the last 5 images waited 7 hours. This version includes the fixes. See the [case study](../case-studies/dragon-coins-overnight-build.md).
> - **Design-debate mode**, the **durable wake-up** and the **finish handshake** are a design that hasn't been tried yet.
> - Tools change quickly. This assumes Claude Code and ChatGPT Agent mode with the GitHub connector. It has two modes:

- **Art mode:** ChatGPT makes images; Claude builds the feature and drops them in.
- **Design-debate mode:** you give an idea; ChatGPT critiques Claude's proposals until they agree on a path; then Claude builds it and ChatGPT reviews it.

It's written from the first real run, in which the art was 100% done by 1:36am, but the last 5 images sat unprocessed for 7 hours because the builder's wake-up timer never fired and nothing noticed.

---

## Part 1: Shared rules (both modes)

### 1.1 The repo

One private repo per project, named `<project>-desk`, for example `myapp-desk`. Code lives in the real app repo; this repo only coordinates.

| File | Who writes it | Purpose |
|---|---|---|
| `PROTOCOL.md` | Claude | This file: the rules |
| `BRIEF.md` | You (Claude drafts it) | The idea, goals, limits, and what Claude may decide without asking |
| `STATE.json` | Both | **The single source of truth.** Every work item and its state |
| `MESSAGES.md` | Both, plus you | The conversation. Add new messages at the bottom; never edit old ones |
| `GPT-LOG.md` | ChatGPT | One line per run |
| `MORNING.md` | Claude | The final summary for you |
| `incoming/` | ChatGPT | Art mode: finished images |
| `references/` | Claude | Locked reference images or examples |
| `DECISION.md` | Claude (ChatGPT signs off) | Design-debate mode: the agreed spec |

### 1.2 STATE.json

Either agent may update it. A work item moves forward only, one state at a time.

```json
{
  "project": "dragon-coins",
  "mode": "art",
  "phase": "building",
  "terminal": null,
  "items": [
    {
      "id": "card-champion",
      "state": "integrated",
      "batch": "ART-06",
      "artistCommit": "cd54b39",
      "builderCommit": "ae0fe6b",
      "notes": ""
    }
  ],
  "heartbeats": { "claude": "2026-10-10T01:45", "chatgpt": "2026-10-10T01:36" },
  "limits": { "chatgpt": { "remaining": "unknown", "resetsAt": null, "checkBackAt": null, "updated": "2026-10-10T01:36" } }
}
```

- **Art states:** `queued → uploaded → validated → reviewed → integrated → complete`, plus `redo` (it goes back to `queued` with a note in MESSAGES.md).
- **Debate states:** `open → proposed → critiqued → agreed → built → reviewed → complete`, plus `needs-human`.
- **`terminal`** stays `null` until the finish handshake (1.5).
- **`heartbeats`:** each agent writes its last run time on every run, even when there's nothing to do. This is how each side can tell the other is alive.
- **A file in `incoming/` counts as `uploaded`** no matter what STATE.json says. Files beat bookkeeping.

### 1.3 Wake-ups (the part that failed last time)

**Rule: a wake-up only counts once you've seen it fire.**

| Agent | How it wakes | Schedule |
|---|---|---|
| ChatGPT | Scheduled task in the same chat (Agent mode) | `:00` and `:30` |
| Claude | **A trigger that survives the chat session:** a GitHub Action that runs Claude Code when this repo changes (best), or Claude's durable scheduled tasks. **Never** session-only timers alone. | `:15` and `:45`, plus on every push |

- **Skip a run if the last one is still going.** Never stack batches.
- **Never turn off a wake-up that is working.** Only add backups.
- **Stay quiet when nothing changed:** just update your heartbeat.

### 1.4 Bedtime checklist

Claude doesn't say goodnight until every box is ticked:

- [ ] BRIEF.md has your goals, limits and pre-approved decisions, and you've answered any open questions.
- [ ] STATE.json lists every item.
- [ ] Claude's wake-up has **fired once for real** and written `heartbeat OK` to MESSAGES.md, and you saw it.
- [ ] ChatGPT has done one run and written its heartbeat.
- [ ] The work is on a branch, and Claude has confirmed the host doesn't deploy branches (e.g. on Netlify, only the production branch builds).
- [ ] If the trigger runs on your computer, it's plugged in and kept awake (on a Mac: `caffeinate -i -s -t 43200`).

### 1.5 The finish handshake

1. Claude finishes everything, tests it, and posts **`FINAL INTEGRATION COMPLETE`** in MESSAGES.md with the commit ID. Claude then sets `terminal: "claude-done"`.
2. ChatGPT checks it (a quick look in art mode, a full review in debate mode). It posts **`CONFIRMED COMPLETE`** and sets `terminal: "complete"`.
3. Only then does each side stop its schedule.
4. **The watchdog:** if either side's heartbeat is more than 90 minutes old while work is still open, the other side posts `⚠️ <agent> silent since <time>` at the top of MESSAGES.md and in its log. (If it can notify you directly, it does that too.) It keeps doing its own work.
5. Claude writes **MORNING.md** for you:
   - what got done, with commit IDs
   - what didn't, and why
   - decisions made, and the ones waiting on you
   - how to try it: the preview URL and steps
   - the exact words you say to ship it

### 1.6 Messages

- Heading format: `### <From> → <To> · <batch or round ID> · <commit ID>`. The batch ID and commit ID give the order, not the clock.
- Keep messages short: what changed, what you need, and any question.
- Your messages (`### Human → both`) override everything else.

### 1.7 Limits (both modes)

- **Never without you:**
  - publish or merge to `main`
  - spend money
  - change the database structure or delete data
  - send messages to anyone
  - grow the scope beyond BRIEF.md
- Anything that hits a limit → the item goes to `needs-human`, it's posted in MESSAGES.md, and the agents keep working on everything else.
- ChatGPT only edits its own files: `incoming/`, `MESSAGES.md`, `GPT-LOG.md`, and its fields in `STATE.json`.

---

### 1.8 Usage limits (learned the hard way)

Image work burns through ChatGPT's usage fast, and an agent that runs out goes silent. Each agent records its limits **before** it runs out, so the other side knows when to look again.

- ChatGPT keeps `STATE.json` → `limits.chatgpt` up to date: `remaining` (or "unknown"), `resetsAt`, `checkBackAt` (reset + 3 minutes), and `updated`.
- Before stopping, it writes `PAUSED until <reset> · check back <reset + 3 min>` in GPT-LOG.md and MESSAGES.md.
- **ChatGPT checks back 2–3 minutes after its reset.** It schedules its next run for `checkBackAt` if it can; if it can't, it says so.
- **Claude also looks at `checkBackAt`.** It schedules one durable check for that time. If nothing has happened 15 minutes after it, Claude posts a nudge, and tells the human if it can.
- Keep batches small (at most 2 images per run) so a run never dies halfway through an upload.

ChatGPT's full instructions, including this rule, are in [`agents/CHATGPT.md`](../agents/CHATGPT.md). Point ChatGPT at that file instead of pasting long prompts.

## Part 2: Art mode

### 2.1 Flow

The order of steps:

1. Claude writes the plan and an `ART-QUEUE.md` (file names, sizes, style blocks, prompts).
2. Claude builds the feature with stand-in art, so new images are drop-in swaps.
3. ChatGPT makes **at most 2 images per run**: it checks them, uploads them, re-checks the uploads, and updates STATE.json and the log.
4. Claude, woken by the push, runs **one command** (`npm run import-art`). The command converts the images and registers them automatically, with no code edits per image. Claude checks them in the preview, commits, marks them `integrated`, and replies.
5. When the queue is empty, they do the finish handshake.

### 2.2 Art rules (measurable, not vibes)

- Exact pixel sizes, and transparency where asked.
- No text, letters, numbers, runes, logos, borders or frames.
- **Protected areas as pixel ranges**, e.g. for a 1024×1536 legendary card, rows 0–229 and 1152–1535 contain no main subject.
- **A locked character reference:** the first approved hero image is copied to `references/`, and every later image matches it.
- **Upload safety:**
  - Keep each file under the tested safe size (under ~700 KB worked for us) by re-encoding without resizing.
  - After uploading, re-read the file and check that it's a complete PNG at the right size (signature, chunks, end marker, dimensions).
- One regeneration at most per image, with one specific fix.

### 2.3 ChatGPT prompt (art mode)

```text
You are the art agent for <project>. Use ONLY the GitHub connector, never the website, on repo <owner>/<project>-desk. Read PROTOCOL.md (art mode) first; it overrides anything else except the human's messages.

Each run:
1. If your previous run is still going, stop. Write your heartbeat in STATE.json.
2. Read MESSAGES.md, STATE.json, ART-QUEUE.md and the incoming/ listing. Do Claude's redo requests first.
3. Make at most 2 images that are queued and missing from incoming/. Put the style block in front of each prompt. Match references/ for any character. Follow the size, transparency and protected-pixel rules exactly. Inspect each one, and regenerate at most once with one specific fix.
4. Re-encode to the safe size without resizing, upload to incoming/ in one commit "Art <BATCH-ID>: <files>", then re-read every file and check it's a complete PNG at the right size. Fix any that fail.
5. Update your items in STATE.json to "validated". Add one message to MESSAGES.md (batch ID, commit, any questions) and one line to GPT-LOG.md.
6. Watchdog: if Claude's heartbeat is more than 90 minutes old while items are waiting, post "⚠️ Claude silent since <time>".
7. If you're about to hit a usage limit, first write "PAUSED until <time>" in GPT-LOG.md.

Stop your schedule only after Claude posts FINAL INTEGRATION COMPLETE and you've posted CONFIRMED COMPLETE. Only edit incoming/, MESSAGES.md, GPT-LOG.md and your fields in STATE.json.
```

---

## Part 3: Design-debate mode

### 3.1 Flow

The order of steps:

1. **You post the idea** in BRIEF.md: the goal, who it's for, and the limits. Before bed, Claude asks you up to 3 questions and adds the answers.
2. **Criteria first (round 0).** Claude proposes how "best" will be judged, with weights, e.g.:
   - kids' delight 30%
   - parent effort 20%
   - simplicity to build 20%
   - risk to existing data 20%
   - cost 10%

   ChatGPT may adjust it once. It's frozen after that.
3. **Up to 3 debate rounds** in MESSAGES.md (`ROUND-1`, `ROUND-2`, `ROUND-3`):
   - **Claude proposes** 2–3 options, each a short paragraph covering how it works, what it touches in the code, and the main risk.
   - **ChatGPT critiques.** Its job is to find holes, not to agree:
     - edge cases
     - a simpler option nobody has mentioned
     - what a real kid or parent would actually do
     - what could break existing data

     It scores every option against the criteria and must name at least one real weakness in the leading option.
   - **Claude responds:** it revises, merges, or drops options.
4. **Deciding:**
   - If both score the same option highest → it's agreed.
   - If they still disagree after round 3 → Claude decides and writes ChatGPT's objection into DECISION.md under "Dissent".
   - If the best option needs something outside BRIEF.md's limits → `needs-human`. **Build the best option that stays inside the limits**, and leave the bigger version for you.
5. **DECISION.md** (Claude writes it; ChatGPT replies `SIGNED OFF` or names specific gaps). It holds:
   - what we're building, as a short spec with acceptance checks ("a kid can… / a parent sees…")
   - what we rejected and why
   - what's out of scope
   - dissent, if any
   - risks and how we'll test them
6. **Build.** Claude codes it on a branch, tests it, and pushes.
7. **Review.** ChatGPT reads the changes, which Claude links or summarizes in MESSAGES.md, and checks them against DECISION.md's acceptance checks. It posts `REVIEW: PASS` or a numbered list of fixes. There's at most 2 review rounds.
8. **The finish handshake and MORNING.md**, which also says which decisions you should double-check.

### 3.2 Debate rules

- **No polite agreement.** Two AIs agreeing doesn't make something right. Every critique names a real weakness or explains why there's none.
- **Concrete over clever.** Options must say what changes in the app, not only how it feels.
- **Your word wins.** A `Human → both` message at any point overrides the debate.
- **Hard limit:** nothing that touches real data, money, publishing, or other people gets decided overnight.

### 3.3 ChatGPT prompt (design-debate mode)

```text
You are the critic and reviewer for <project>. Use ONLY the GitHub connector on repo <owner>/<project>-desk. Read PROTOCOL.md (design-debate mode) and BRIEF.md first.

Each run:
1. If your previous run is still going, stop. Write your heartbeat in STATE.json.
2. Read MESSAGES.md, STATE.json, BRIEF.md and DECISION.md if it exists. Find what's waiting on you.
3. Depending on the phase:
   - CRITERIA: accept Claude's criteria or adjust them once, with reasons.
   - DEBATE: for each option, list edge cases, a simpler alternative if there is one, what a real kid or parent would do, and risks to existing data. Score every option against the criteria. You must name at least one real weakness in the leading option. Don't agree just to be agreeable.
   - DECISION: reply SIGNED OFF, or list specific gaps against BRIEF.md.
   - REVIEW: check Claude's build against every acceptance check in DECISION.md. Reply REVIEW: PASS, or give numbered fixes.
4. Post your reply in MESSAGES.md with the round ID, and update STATE.json and GPT-LOG.md.
5. Watchdog: if Claude's heartbeat is more than 90 minutes old while it's Claude's turn, post "⚠️ Claude silent since <time>".
6. Flag anything that needs the human (money, data, publishing, scope) as needs-human. Never approve it yourself.

Stop only after you've posted CONFIRMED COMPLETE following Claude's FINAL INTEGRATION COMPLETE. Only edit MESSAGES.md, GPT-LOG.md and your fields in STATE.json.
```

---

## Part 4: Claude kickoff prompt (either mode)

Paste this to Claude Code:

```text
Overnight run, <art | design-debate> mode, project <name>. Follow PROTOCOL.md in <owner>/<project>-desk.

Before I go to sleep:
1. Ask me up to 3 questions and put my answers in BRIEF.md.
2. Set up STATE.json and the desk repo.
3. Set up a wake-up that survives this chat session, fire it once, and show me "heartbeat OK".
4. Confirm the branch won't deploy.

Then work until FINAL INTEGRATION COMPLETE and CONFIRMED COMPLETE, and write MORNING.md.

Pre-approved: <list>. Never without me: publishing or merging to main, money, data changes, scope growth.
```
