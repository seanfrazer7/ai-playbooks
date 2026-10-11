# Claude Code: platform notes

Read [`START-HERE.md`](../START-HERE.md) first. This file only covers what's specific to Claude Code.

## Abilities

- **Desk:** full access through `git` and `gh`. Claude Code is the best **lead**.
- **Usage:** Pro and Max plans have a rolling 5-hour session window and a weekly cap. Claude Code shares them with claude.ai chats. `/usage` shows them, and a limit message gives the exact reset time. With an API key, there's no window, just your spend limit.
- **Notifying the human:** the desktop app can send push notifications. Otherwise the watchdog issue email or ntfy.

## Wake-ups, most durable first

1. **GitHub Action on the desk** ([`claude-wake.yml`](../templates/desk/.github/workflows/claude-wake.yml)). Runs on GitHub's servers on a schedule, on every push, and when the watchdog asks. Doesn't need your computer. Needs a `CLAUDE_CODE_OAUTH_TOKEN` secret (from `claude setup-token`, uses your plan) or `ANTHROPIC_API_KEY` (API billing).
2. **Cloud routines** (`/schedule` in Claude Code). Hosted by Anthropic on a schedule. In research preview as of 2026; check the current docs.
3. **Scheduled tasks in the Claude desktop app.** Run on your computer, so it must stay on and awake.
4. **Backup only:** `/loop`, `Monitor`, or timers inside one session. They stop when the session ends. **In v1 they never fired overnight.** Never rely on them alone.

**Pick one primary.** If you use the GitHub Action, don't also run a local session as the same agent ID, or two Claudes will edit the same status file. A local session can still be the human's "control room" for setup and questions.

## Lead setup checklist (Claude Code specific)

1. `gh repo create <owner>/<project>-desk --private`, then copy `templates/desk/` in, plus `START-HERE.md` and `protocols/two-agent-desk.md` as `PROTOCOL.md`.
2. Rename `status/AGENT-ID.json` to one file per agent, and fill in `STATE.json`.
3. If you're using the Action: ask the human to add the secret (never handle the token yourself), then run it once with `gh workflow run claude-wake.yml` and wait for the heartbeat.
4. Run the watchdog once with `gh workflow run watchdog.yml`, and show the human the result.
5. Confirm the work branch doesn't deploy (e.g. the host only builds `main`).

## Usage tips

- When `/usage` shows under about 15% of the session window left, write the pause note.
- If both agents are Claude on one plan, they share the window. Set `config.sharedPool: true`, and keep the partner's runs light.
- Each Action run uses a fresh environment. All memory has to be in the desk (rule S10).
