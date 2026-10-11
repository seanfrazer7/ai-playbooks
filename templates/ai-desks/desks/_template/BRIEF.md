# Brief: <project>

*The lead drafts this with the human. Only humans change it after setup.*

## Goal
<One or two sentences: what "done" looks like.>

## Acceptance checks
The run is done when all of these are true:
1. <A user can… / The report contains… / The tests in … pass>
2. …

## Agents
| ID | Platform | Role | Human who owns it | Wakes |
|---|---|---|---|---|
| `claude` (lead) | Claude Code | builder | <name> | :00 and :30, plus every push |
| `chatgpt` | ChatGPT Agent mode | reviewer | <name> | :15 and :45 |

Playbook: <build + review | build + art | propose + critique | split the work | research + verify>

## Where the work happens
- App repo and branch: `<owner>/<repo>` on `<branch>` (doesn't deploy: <how we checked>)
- Desk: this repo

## Agents may decide alone
- <e.g. anything on the branch that doesn't touch real data, money, publishing or other people>
- Cover mode allowed: <yes | no>

## Needs a human (never decided by agents)
- Merging to `main`, publishing, deploying
- Spending money beyond the budget below
- Database structure changes, deleting data, real users' data
- Sending anything outside the desk
- New accounts, keys, connectors or permissions
- Growing the scope beyond this brief
- <anything else>

## Deadline and budget
- Deadline (UTC): <2026-10-11T14:00:00Z | none>
- Most runs per agent: <60>
- API spend limit: <$ | n/a>

## How to reach the human
- GitHub issue "Desk watchdog" in this repo (emails the owner)
- ntfy topic (optional, set as the `NTFY_TOPIC` Actions secret): <yes | no>

## Setup answers
<The lead's questions and the human's answers, word for word.>
