# Claude Code: platform notes

Read [`START-HERE.md`](../START-HERE.md) first. This file only covers what's specific to Claude Code.

## Abilities

- **Desk:** full access through `git` and `gh`. Claude Code is the best **lead**.
- **Usage:** Pro and Max plans have a rolling 5-hour session window and a weekly cap. Claude Code shares them with claude.ai chats. `/usage` shows them, and a limit message gives the exact reset time. With an API key, there's no window, just your spend limit.
- **Notifying the human:** the desktop app can send push notifications. Otherwise the watchdog issue email or ntfy.

## Wake-ups, most durable first

1. **GitHub Action in your `ai-desks` repo** ([`claude-wake.yml`](../templates/ai-desks/.github/workflows/claude-wake.yml)). Runs on GitHub's servers on a schedule, when the partner pushes, and when the watchdog asks, so your computer can be off. It uses your **Claude plan** through a `CLAUDE_CODE_OAUTH_TOKEN` secret, which the human adds **once** for all projects ([one-time setup](../templates/ai-desks/README.md#one-time-setup)).
2. **Cloud routines** (`/schedule` in Claude Code). Hosted by Anthropic, using your plan, with no secret. In research preview as of 2026. The watchdog can't restart one, so it can only email you.
3. **Scheduled tasks in the Claude desktop app.** Use your plan, need no secret, and the lead can create them itself. But they run on your computer, so it must stay on and awake, and the watchdog can't restart them.
4. **Backup only:** `/loop`, `Monitor`, or timers inside one session. They stop when the session ends. **In v1 they never fired overnight.** Never rely on them alone.

**Pick one primary.** If you use the GitHub Action, don't also run a local session as agent `claude` on the same desk, or two Claudes will edit the same status file. A local session can still be the human's "control room" for setup and questions.

## Lead setup checklist (Claude Code specific)

1. **First time only:** if `<owner>/ai-desks` doesn't exist, create it as a **private** repo from [`templates/ai-desks/`](../templates/ai-desks/README.md). Then walk the human through the one-time setup. **The human runs `claude setup-token` and `gh secret set` themselves. Never ask for the token, and never handle it.**
2. Copy `desks/_template/` to `desks/<project>/`. Add `START-HERE.md`, and `protocols/two-agent-desk.md` as `PROTOCOL.md`.
3. Rename `status/AGENT-ID.json` to one file per agent. Fill in `STATE.json`, including `appRepo` and `appBranch`, and keep `"wakeWorkflow": "claude-wake.yml"` for `claude`. If the app's build or test commands aren't in the workflow's `--allowedTools` line yet, add them.
4. Commit and push. Then `gh workflow enable claude-wake.yml`, `gh workflow enable watchdog.yml`, and `gh workflow run claude-wake.yml -f desk=<project>`. Wait for the heartbeat in `desks/<project>/status/claude.json`.
5. Run the watchdog once (`gh workflow run watchdog.yml`), and show the human the result.
6. Confirm the work branch doesn't deploy (e.g. the host only builds `main`).

## Auto mode and permission prompts

Claude Code's auto mode blocks actions that look risky and that the human didn't ask for. In the first test run it blocked `gh secret list` on `ai-desks` as "credential exploration", then stopped for input after 3 blocks. To avoid that:
- Never list or check secrets. Run the workflow and read its log instead.
- The start message should name the repos ("My repos for this: …"). If it doesn't, ask the human once to confirm them in a typed message.
- If something is blocked, don't retry it with different commands. Tell the human what was blocked and what one sentence from them would allow it.

## Usage tips

- When `/usage` shows under about 15% of the session window left, write the pause note.
- If both agents are Claude on one plan, they share the window. Set `config.sharedPool: true`, and keep the partner's runs light.
- Each Action run uses a fresh environment. All memory has to be in the desk (rule S10).
- Every desk in `ai-desks` shares your one Claude limit, and so do your normal chats. The workflow runs one desk at a time. If you're chatting with Claude a lot during the day, expect desks to pause sooner.
