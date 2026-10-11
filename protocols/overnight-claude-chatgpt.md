# Claude ⇄ ChatGPT overnight presets

Two ready-made playbooks for the [two-agent desk protocol](two-agent-desk.md), where Claude Code is the lead and builder and ChatGPT is the artist or critic. **The shared rules (desk, state, wake-ups, usage limits, watchdog, finishing) are in the main protocol.** This file covers only what's specific to each preset.

To start one: follow [`START-HERE.md`](../START-HERE.md), and tell the lead "Playbook: build + art" or "Playbook: propose + critique".

> **Status (Oct 2026):**
> - **Art mode** ran once for real. The art finished 20/20 and the code was complete, but the builder's wake-up failed, so the last 5 images waited 7 hours ([case study](../case-studies/dragon-coins-overnight-build.md)). The main protocol's wake-up rules, proof-of-life check and watchdog are the fixes.
> - **Design-debate mode** is a design that hasn't been tried yet.

---

## Part 1: What changed since v1

| v1 | Now |
|---|---|
| ChatGPT pasted a long prompt | Both agents are pointed at [`START-HERE.md`](../START-HERE.md) |
| Heartbeats and limits lived in `STATE.json` | Each agent has its own `status/<id>.json`, so they don't overwrite each other |
| `GPT-LOG.md` | `status/chatgpt.json` → `lastResult` and `next`, plus messages |
| `FINAL INTEGRATION COMPLETE` | `FINAL COMPLETE <commit>`, then `CONFIRMED COMPLETE` |
| `MORNING.md` | `REPORT.md` |
| Agents watched each other | Agents watch each other, **and** a GitHub watchdog that uses no AI emails you |
| ChatGPT ran into its usage limit | Pause notes before running out, a `checkBackAt` time, and cover mode |

## Part 2: Art mode

**Playbook:** build + art. Claude (`claude`, lead) builds the feature and drops images in. ChatGPT (`chatgpt`) makes images.

### 2.1 Flow

1. Claude writes `work/ART-QUEUE.md`: file names, exact sizes, transparency, protected pixel regions, one shared style block, and a prompt for each image. Each image is an item in `STATE.json` with `"next": "chatgpt"`.
2. Claude builds the feature with stand-in art first, so every new image is a drop-in swap and the code never waits on the art.
3. ChatGPT makes **at most 2 images per run**: it checks them, uploads them to `work/incoming/`, re-reads the uploads, then sets each item to `review` with `"next": "claude"`.
4. Claude, woken by the push, runs **one command** (e.g. `npm run import-art`) that converts and registers the images with no code edits per image. It checks them in the preview, commits to the branch, and sets each item to `done`, or to `redo` with `"next": "chatgpt"` and one specific fix.
5. When every item is `done`, Claude posts `FINAL COMPLETE`, and ChatGPT takes a final look and posts `CONFIRMED COMPLETE` ([protocol §9](two-agent-desk.md#9-finishing)).

### 2.2 Art rules (measurable, not vibes)

- Exact pixel sizes, and transparency where asked.
- No text, letters, numbers, runes, logos, borders or frames.
- **Protected areas as pixel ranges.** E.g. for a 1024×1536 legendary card, rows 0–229 and 1152–1535 contain no main subject.
- **A locked character reference.** The first approved hero image is copied to `work/references/`, and every later image matches it. Claude's feedback names concrete features ("big amber eyes, rounded snout, never menacing").
- **Upload safety:**
  - Keep each file under the tested safe size (under about 700 KB worked) by re-encoding without resizing.
  - After uploading, re-read each file and check that it's a complete PNG at the right size.
- At most one regeneration per image per run, with one specific fix. After 3 attempts, the item is parked (rule S4).
- Do Claude's `redo` items first.

## Part 3: Design-debate mode

**Playbook:** propose + critique. Claude (`claude`, lead) proposes and builds. ChatGPT (`chatgpt`) critiques and reviews.

### 3.1 Flow

Each step is an item in `STATE.json` (`criteria`, `round-1`, `round-2`, `round-3`, `decision`, `build`, `review-1`, `review-2`), so it's always clear whose turn it is.

1. **The idea.** The human's goal and limits are in `BRIEF.md`. During setup, Claude asks up to 5 questions and records the answers.
2. **Criteria first.** Claude proposes how "best" will be judged, with weights, e.g.:
   - kids' delight 30%
   - parent effort 20%
   - simplicity to build 20%
   - risk to existing data 20%
   - cost 10%

   ChatGPT may adjust it once. It's frozen after that.
3. **Up to 3 debate rounds:**
   - **Claude proposes** 2–3 options, each a short paragraph covering how it works, what it changes in the code, and the main risk.
   - **ChatGPT critiques.** Its job is to find holes, not to agree:
     - edge cases
     - a simpler option nobody has mentioned
     - what a real user would actually do
     - what could break existing data

     It scores every option against the criteria, shows the weighted totals, and must name at least one real weakness in the leading option.
   - **Claude responds:** it revises, merges or drops options.
4. **Deciding:**
   - If both score the same option highest, it's agreed.
   - If they still disagree after round 3, Claude decides and writes ChatGPT's objection under "Dissent" (rule S5).
   - If the best option needs something outside `BRIEF.md`'s limits, that item goes to `blocked`. **Build the best option that stays inside the limits**, and leave the bigger version for the human.
5. **`work/DECISION.md`.** Claude writes it; ChatGPT replies `SIGNED OFF` or names specific gaps. It holds:
   - what we're building, as a short spec with acceptance checks ("a kid can… / a parent sees…")
   - what we rejected and why
   - what's out of scope
   - dissent, if any
   - risks and how we'll test them
6. **Build.** Claude codes it on a branch, tests it, and pushes.
7. **Review.** ChatGPT checks the changes against every acceptance check, then posts `REVIEW: PASS` or a numbered list of fixes. There are at most 2 review rounds.
8. **Finish** with the handshake and `REPORT.md`, which also lists the decisions the human should double-check.

### 3.2 Debate rules

- **No polite agreement.** Two AIs agreeing doesn't make something right.
- **Concrete over clever.** Options must say what changes in the app, not only how it feels.
- **The human's word wins.** A `### Human → …` message at any point overrides the debate.
- **Hard limit:** nothing that touches real data, money, publishing or other people gets decided by the agents.
