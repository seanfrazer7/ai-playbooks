# Platforms

Every agent on a desk needs three abilities:

1. **Read the desk** (a private GitHub repo)
2. **Write to the desk** (commit files)
3. **Wake itself up** on a schedule that keeps running after the chat ends

An agent missing ability 3 still works, but only while a human keeps poking it. An agent missing ability 2 can't take part.

| Platform | Read + write desk | Wakes itself | Can see its usage | Best role | Notes |
|---|---|---|---|---|---|
| [Claude Code](CLAUDE-CODE.md) | Yes (git, `gh`) | Yes: GitHub Action, cloud routine, or desktop scheduled task | Yes (`/usage`, limit messages) | **Lead**, builder | Best lead: can create the desk and run the watchdog |
| [ChatGPT](CHATGPT.md) | Yes, in Agent mode with the GitHub connector | Yes: scheduled tasks | Partly (limit messages) | Artist, critic, reviewer | Proven in v1 for art. Confirm the connector can write from a scheduled run |
| [Gemini](GEMINI.md) | Yes with Gemini CLI; the Gemini app isn't confirmed | Yes: Gemini CLI in a GitHub Action | API quota page | Builder, reviewer, researcher | Use the CLI or the Action, not the chat app |
| [Grok](GROK.md) | GitHub connector exists; writing isn't confirmed | Grok Automations (scheduled) | Limit messages | Critic, researcher | Test writing during proof of life |
| [Anything else](OTHER.md) | Depends | Depends | Depends | Any | Also covers two threads of one model, and a friend's agent |

**Checked October 2026.** These products change monthly. The proof-of-life check ([protocol §8](../protocols/two-agent-desk.md#8-proof-of-life-before-the-human-leaves)) is what actually confirms a setup works. If a row here is wrong for you, please [open an issue](../CONTRIBUTING.md).

## Picking the lead

The lead creates the desk, breaks ties and writes the report. Pick the agent that:
1. can run commands and create a repo (so it can set up the desk and watchdog), and
2. has the most reliable wake-up.

That's usually Claude Code, or Gemini CLI / Codex CLI. A chat-only agent (ChatGPT, Grok, the Gemini app) works best as the partner.

## The universal fallback

Any model with an API can be a desk agent by running inside a GitHub Action on the desk repo: on a schedule, on every push, and when the watchdog asks. [`claude-wake.yml`](../templates/desk/.github/workflows/claude-wake.yml) is the pattern. Swap in the vendor's own action or CLI (e.g. `google-github-actions/run-gemini-cli`, OpenAI's Codex CLI). This costs API money, so set a spend limit with the vendor and a `budget` in `BRIEF.md`.
