---
name: ask-gpt
description: Get a live second opinion from GPT (through the Codex CLI, read-only) on Claude's work before acting on it, such as a "what has to be true" analysis, a plan, a draft, numbers in a spreadsheet, or code. Use when the user asks Claude to check with GPT, have GPT review or critique something, or get a second opinion, or says "ask GPT". Claude drafts, GPT critiques, Claude revises, and Claude only applies changes after the user agrees.
argument-hint: <what to work on, and what GPT should check>
---

# Ask GPT

You (Claude) do the work. GPT, through the Codex CLI on this computer, is the **checker**: it critiques your draft and sharpens the goal. Then you revise, and you only change the real thing (a sheet, a doc, code) after the human agrees.

Typical use: the human is in a Google Sheet and says "Work out what has to be true for this goal, and have GPT check it."

## Rules
- **GPT gets only what you send it.** It can't see the sheet, your files, or the human's ChatGPT history. Send the goal, the relevant numbers and your draft, and nothing else.
- **Never send** passwords, keys, tokens, or anything the human marked private. For a work file, ask before sending its contents to GPT; it goes to OpenAI.
- **GPT is read-only.** It answers; it never edits. You make every change, after the human's OK.
- **GPT is a reviewer, not the boss.** Weigh what it says. Say where you disagree and why.

## Steps

1. **Understand the goal and gather the inputs.** Read what you need (the sheet range, the doc, the code). If the goal is unclear, ask one short question first.
2. **Draft your answer.** For "what has to be true": list the conditions that would have to hold for the goal to be met, with the numbers they imply, and show the math.
3. **Ask GPT.** Write a self-contained request: the goal in one or two sentences, the inputs it needs (a small table is fine), your draft, and what to check. For example: "Critique this. What's wrong, missing or unrealistic? Is the goal itself clear? Answer in at most 6 bullets, most important first." Run it from an empty temporary folder, so Codex can't see any local files:

   ```bash
   d=$(mktemp -d) && cd "$d" && printf '%s' "<request>" | codex exec --sandbox read-only --ephemeral --skip-git-repo-check --color never -o "$d/answer.md" - > "$d/log.txt" 2>&1; cat "$d/answer.md"; cd - >/dev/null; rm -rf "$d"
   ```

   A reply usually takes 5 to 60 seconds. If `answer.md` is empty, read `log.txt`: "not logged in" means the human should run `codex` once in Terminal and sign in with ChatGPT. If `codex` isn't installed, tell the human (`npm install -g @openai/codex`) and offer to continue without GPT.
4. **Show the human both views, briefly.** Your draft (short), GPT's points, and what you'd change because of them (and where you disagree). One more round with GPT is fine if its points changed the answer a lot. Stop after two rounds.
5. **Ask before changing anything.** For example: "Want me to write this into the sheet, in columns D to F?" Then make the edit with whatever access you have (for a Google Sheet, the Google connector in Claude). Keep what was there unless the human said to replace it, and say exactly what you changed.

## If GPT should know more about the human's goal
Ask the human for any context GPT should have (who it's for, constraints, what "good" means) and put it in the request. Codex runs on the human's ChatGPT account, but it doesn't see their past ChatGPT chats or custom instructions.
