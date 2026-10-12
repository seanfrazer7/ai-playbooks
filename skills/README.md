# Skills: quick install

Claude Code skills for getting Claude and GPT to work together. For Macs; personal, non-confidential work ([why](../protocols/two-agent-desk.md#suitable-use-and-data)).

| Skill | Use it for | Setup |
|---|---|---|
| [`ask-gpt`](ask-gpt/SKILL.md) | A quick second opinion **while you work**. Claude drafts, GPT checks it in seconds, and Claude applies it after your OK | None beyond signing in |
| [`local-desk`](local-desk/SKILL.md) | Hand off a bigger job. Claude and Codex take turns on timers **while you're away**, and you're told when it's done | A one-time setup on each Mac (the skill walks you through it) |
| [`overnight-handoff`](overnight-handoff/SKILL.md) | The GitHub version, with ChatGPT in Agent mode | See [START-HERE](../START-HERE.md) |

## Install

In Terminal:

```bash
git clone --depth 1 https://github.com/seanfrazer7/ai-playbooks ~/Downloads/ai-playbooks && mkdir -p ~/.claude/skills && cp -R ~/Downloads/ai-playbooks/skills/ask-gpt ~/Downloads/ai-playbooks/skills/local-desk ~/.claude/skills/
```

To update later: `git -C ~/Downloads/ai-playbooks pull`, then run the `cp` part again.

## What you need

1. **Claude Code**, installed and logged in.
2. **Codex** (OpenAI's coding agent, which runs GPT), installed and signed in. Install it with `npm install -g @openai/codex` if needed, then run `codex` once in Terminal and choose "Sign in with ChatGPT". You sign in yourself; the skills never handle your logins.
3. **For Google Sheets or Docs:** the Google connector turned on for Claude in your Claude settings.

## Use

- `/ask-gpt Work out what has to be true for the goal in my budget sheet, and have GPT check it.`
- `/local-desk <your goal>`. The first time on each Mac, it walks you through the one-time setup and a proof of life. After that, it's one message per goal. `/local-desk status` lists your desks, and `/local-desk stop <name>` turns one off.

## Before you use it at work

- **What Claude sends GPT goes to OpenAI**, and what Claude reads goes to Anthropic. Check that your company allows that for the data you're working with.
- **Use your work accounts** if your company provides Claude or ChatGPT accounts.
- **Managed Macs** may block the background timers `local-desk` needs. `ask-gpt` doesn't use timers.

Each person uses their own accounts and usage. Installing these doesn't connect to anyone else's computer, account or desks.
