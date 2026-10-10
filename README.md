# ai-playbooks

**How I build real software with AI agents: case studies, honest post-mortems, and the protocols, prompts and Claude Code skills that came out of them.**

I'm Sean Frazer. I build products by directing AI agents. I set the goals and the limits, the agents do the engineering, and I measure what actually happens. This repo is where I write that down, including the parts that didn't work.

---

## Highlights

- **A feature built overnight by two AIs.** Claude Code wrote a coin economy, a market and holo trading cards. ChatGPT painted 20 matching card illustrations. They talked to each other only through Markdown files in a GitHub repo. → [Case study](case-studies/dragon-coins-overnight-build.md)
- **A real app my kids use every school day.** Course Quest turns an overdue-homework backlog into one small daily quest, with AI course import, streaks, a dragon to raise, and parent-controlled rewards. → [Case study](case-studies/course-quest.md)
- **Post-mortems from both AIs, compared.** Each one found the half of the failure the other missed. → [Read the comparison](case-studies/dragon-coins-overnight-build.md#two-post-mortems-compared)

![Card Binder from Course Quest](case-studies/assets/card-binder.jpg)

## What's here

| Folder | What's inside |
|---|---|
| [`case-studies/`](case-studies/) | Real projects: the problem, the setup, a timeline, the results, what broke, what changed |
| [`protocols/`](protocols/) | Reusable playbooks. Start with the [overnight Claude ⇄ ChatGPT protocol](protocols/overnight-claude-chatgpt.md) |
| [`prompts/`](prompts/) | Copy-paste prompts for each agent's role |
| [`agents/`](agents/) | Start-here instruction files for each agent. Point ChatGPT at [`agents/CHATGPT.md`](agents/CHATGPT.md) |
| [`skills/`](skills/) | Claude Code skills you can install, e.g. [`overnight-handoff`](skills/overnight-handoff/SKILL.md) |

## Use the overnight protocol

1. Create a private `<project>-desk` repo and copy [the protocol](protocols/overnight-claude-chatgpt.md) into it as `PROTOCOL.md`.
2. Paste the [Claude kickoff prompt](prompts/claude-overnight-kickoff.md) into Claude Code in your app repo. Point ChatGPT (Agent mode + GitHub connector) at [`agents/CHATGPT.md`](agents/CHATGPT.md); the one-line message to send is at the bottom of that file.
3. **Don't go to bed until the bedtime checklist passes.** In particular, the builder's wake-up has to fire once while you watch. That's the lesson from the first run.

To install the skill, copy `skills/overnight-handoff/` into your project's `.claude/skills/` folder (or `~/.claude/skills/` to use it everywhere).

## Principles I work by

- **Agents build; I own the decisions.** Anything touching money, real data, publishing or other people waits for me.
- **Work on branches, ship deliberately.** Nothing deploys without a human "ship it."
- **Measure, then write it down.** Every case study has a timeline and numbers, and says what failed.
- **Test the boring parts first.** Consistent AI art worked on the first try. Waking up on schedule didn't.

## License

Code and skills: [MIT](LICENSE). Writing and images: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use them and credit "Sean Frazer, ai-playbooks."
