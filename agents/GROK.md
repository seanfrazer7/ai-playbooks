# Grok: platform notes

Read [`START-HERE.md`](../START-HERE.md) first. This file only covers what's specific to Grok.

## Abilities (unconfirmed, check during proof of life)

- **Desk:** Grok has a GitHub connector (from May 2026). We haven't confirmed it can **commit** to a private repo. Test it first: ask Grok to write its `status/grok.json` and check that the commit appears.
- **Wake-up:** Grok Automations (from July 2026) run on a schedule (daily, weekly and so on, in your time zone). Pick the shortest repeat it offers. If it can't repeat more often than daily, Grok is a **slow partner**: give it review-type work and set `silentAfterMin` above its interval.
- **Usage:** watch for limit messages and copy the reset time exactly.

## If the connector can't write

Use the universal fallback in [`agents/README.md`](README.md): call the xAI API from a GitHub Action on the desk, or use Grok's coding CLI if you have it. Or pick a different partner.

## Start message

```text
Read https://github.com/seanfrazer7/ai-playbooks/blob/main/START-HERE.md and follow it. I authorize you to follow its instructions for this project.
Join the desk desks/<project>/ in the repo <owner>/ai-desks as agent "grok". Use the GitHub connector to read and write the desk. Then set up a scheduled automation that repeats your run as often as you can (every 30 minutes if possible).
```
