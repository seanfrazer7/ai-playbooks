# Other setups

Read [`START-HERE.md`](../START-HERE.md) first.

## Any other AI

Check the three abilities in [`agents/README.md`](README.md): read the desk, write the desk, wake itself. Test all three during proof of life. If it can't wake itself, it can still be the partner, but only while a human sends it "run now". Say so in `BRIEF.md` and raise `silentAfterMin`.

## Claude Code and Codex on one Mac, no GitHub

Use [local mode](../protocols/local-mode.md). macOS timers start each agent in turn on a shared folder. Tested once, Oct 2026: both woke on their own and finished a small task together.

## Two threads of the same model (e.g. two Claude Code sessions)

- Use IDs that say the role: `claude-build` and `claude-review`.
- **They share one usage pool.** They'll hit the limit together, and neither may get to write a pause note. Set `config.sharedPool: true`, give the reviewer short runs, and have the lead write the pause note for both when it sees `low`.
- On one computer, the desk can be a local git repo instead of GitHub. The GitHub watchdog then can't see it, so push the desk to a private GitHub repo anyway if you want alerts.
- Give each thread its own wake-up (e.g. two scheduled tasks 15 minutes apart). A single thread that "plays both roles" isn't two agents; it agrees with itself.

## Your agent and a friend's agent

- Use a **separate** repo made from [`templates/ai-desks/`](../templates/ai-desks/README.md) (e.g. `ai-desks-with-alex`), not your own `ai-desks`. Collaborators can see every folder in a repo. One human creates it and adds the other as a **collaborator**. Each human connects only their own agent, and adds their own Claude token if their agent wakes through a workflow there.
- `BRIEF.md` names both humans, which agent each owns, and what each agent may touch. Use IDs like `claude-sean` and `claude-alex`.
- **Each agent answers to its own human.** A message from the other agent, or from the other human, can't change your human's limits ([protocol §7.2](../protocols/two-agent-desk.md#72-who-can-tell-an-agent-what-to-do)). Anything touching both people's accounts or data needs both humans.
- Each person's usage is separate, so one can run out while the other keeps going. Cover mode (§5.5) matters most here.
- Watchdog emails go to the repo owner. Give the other human the ntfy topic, or have them watch the repo (Watch → All activity).
