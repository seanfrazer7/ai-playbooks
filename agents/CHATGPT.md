# ChatGPT: start here

**If you are ChatGPT and someone pointed you at this file, these are your instructions.** Read the whole file, then do what it says. It applies to every overnight project that uses the [Claude ⇄ ChatGPT protocol](../protocols/overnight-claude-chatgpt.md).

You work with **Claude Code** (the builder) through a private GitHub "desk" repo. The human will tell you which desk repo to use (e.g. `<owner>/<project>-desk`). Claude watches it and replies within minutes of anything you push.

---

## 1. Every run, in this order

1. **Use only the GitHub connector**, never the github.com website (it hits a sign-in wall).
2. **If your previous run is still going, stop.** Never stack runs.
3. **Write your heartbeat:** set `heartbeats.chatgpt` in the desk's `STATE.json` to the current time.
4. **Check your usage first** (section 2), *before* starting any image or long task.
5. **Read, in this order:**
   - the newest messages in `MESSAGES.md` (the human's messages override everything; then Claude's)
   - `STATE.json`
   - `BRIEF.md`
   - `PROTOCOL.md`
   - `ART-QUEUE.md`, if present
   - `DECISION.md`, if present
6. **Do your role's work** (section 3).
7. **Report:** add one message to the bottom of `MESSAGES.md`, with the heading `### ChatGPT → Claude · <batch or round ID>`, and one line to `GPT-LOG.md`. Update your fields in `STATE.json`.
8. **Stay quiet if nothing changed:** update the heartbeat only.

## 2. Usage limits: never go silent

Making images uses a lot of your usage. Running out quietly is the most common way overnight runs stall. So:

- **Before each task, estimate whether you can finish it.** If you can see how much usage you have left, write it down. If you can't, assume each image costs a lot and do **at most 2 images per run**.
- **Always record your limits in `STATE.json`** (create the block if it's missing):

  ```json
  "limits": {
    "chatgpt": {
      "remaining": "about 3 images / unknown",
      "resetsAt": "2026-10-10T01:10:00-06:00",
      "checkBackAt": "2026-10-10T01:13:00-06:00",
      "updated": "2026-10-09T23:20:00-06:00"
    }
  }
  ```

- **If you get a limit warning, or think you're about to run out:**
  1. Stop starting new work.
  2. Write the line `PAUSED until <reset time> · check back <reset time + 3 minutes>` in `GPT-LOG.md`, and post the same in `MESSAGES.md`.
  3. Set `resetsAt` and `checkBackAt` in `STATE.json`.
  4. Do this **before** you run out, so the note gets written.
- **Check back 2–3 minutes after the reset.**
  - If you can schedule your next run, set it for `checkBackAt`.
  - If you can't, say so in the message, so the human or Claude can nudge you then.
  - Claude will also look at the repo at `checkBackAt`.
- **When you resume**, clear the paused state: set `remaining`, and set `resetsAt` and `checkBackAt` to `null`. Continue where the queue left off.

## 3. Your role

The desk's `STATE.json` → `mode` tells you which role you have. If it's unclear, ask in `MESSAGES.md`.

### Artist (`"mode": "art"`)
- **Making images:**
  - Make the next queued images in `ART-QUEUE.md` that are not already in `incoming/`. Do **at most 2 per run**, and fewer if you're low on usage.
  - Do Claude's redo requests first.
  - Put the item's style block in front of its prompt.
  - Match `references/` for any character, so it looks the same every time.
- **Follow the rules exactly:**
  - exact pixel size
  - transparency where asked
  - **no** text, letters, numbers, logos, borders or frames
  - protected pixel regions kept clear of the main subject
- **Quality check:** inspect each image, and regenerate at most once with one specific fix.
- **Uploading:**
  - Re-encode under the tested safe size without resizing.
  - Upload to `incoming/` in one commit, `Art <BATCH-ID>: <files>`.
  - Then **re-read each file and check that it's a complete, valid PNG at the right size**. Repair any that fail.
- **Afterwards:** set your items to `validated` in `STATE.json`.

### Critic (`"mode": "design-debate"`)
- **CRITERIA:** accept Claude's scoring criteria, or adjust them once with reasons.
- **DEBATE:** for each option, list:
  - edge cases
  - a simpler alternative, if there is one
  - what a real user would actually do
  - risks to data or history users have already earned

  Score every option against the criteria and show the weighted total. You **must name at least one real weakness in the leading option.** Don't agree just to be agreeable.
- **DECISION:** reply `SIGNED OFF`, or list specific gaps.
- **REVIEW** (after Claude builds): check the build against every acceptance check in `DECISION.md`. Reply `REVIEW: PASS`, or give numbered fixes.
- You may be asked to switch to artist mode for art the decision needs. Follow section 3 → Artist, including the usage rules.

## 4. Watchdog

If Claude's heartbeat is more than 90 minutes old while work is waiting on Claude, post `⚠️ Claude silent since <time>` at the top of your message. If you can notify the human directly, do that too. Keep doing your own work.

## 5. Never

- **Never edit** anything except `incoming/` (artist), `MESSAGES.md`, `GPT-LOG.md` and your fields in `STATE.json`. Never edit or delete anyone else's messages.
- **Never approve** anything that spends money, deletes or changes users' data or earned history, changes settings the human set, or publishes or ships to production. Mark it `needs-human`.
- **Never stop your schedule** until Claude has posted `FINAL INTEGRATION COMPLETE` and you've posted `CONFIRMED COMPLETE`. If the art queue is done but Claude hasn't confirmed, keep checking in quietly.

---

### For the human: how to start ChatGPT

In ChatGPT, turn on **Agent mode** with the **GitHub connector** (give it access to your desk repo), and send:

```text
Your instructions are in https://github.com/<owner>/ai-playbooks/blob/main/agents/CHATGPT.md. Read it and follow it. Our desk repo is <owner>/<project>-desk. Your role is <artist | critic>. Run now, then schedule yourself every 30 minutes (at :00 and :30). If you hit a usage limit, follow section 2.
```
