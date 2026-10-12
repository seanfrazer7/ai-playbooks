# Case study: testing two-agent desks until they actually ran

**October 10–11, 2026 · Claude Code + ChatGPT (GitHub) and Claude Code + Codex (one Mac)**

The [first overnight run](dragon-coins-overnight-build.md) lost seven hours to a wake-up nobody had tested. So I rewrote the protocol for any two agents ([v2](../protocols/two-agent-desk.md)) and then tested it the boring way: small, real tasks, with me watching every wake-up. The tests found eleven problems. This is the list, and what each one changed.

---

## The problem

v1 only worked for Claude and ChatGPT, needed long prompts, and had no answer for an agent running out of usage. I wanted:

- **One message to start.** Point any AI at [`START-HERE.md`](../START-HERE.md), give it a goal, and it sets up everything else.
- **No silent stalls:** every task has an owner, there are hard caps on retries and rounds, and a watchdog that uses no AI.
- **A version that runs on one Mac**, for computers without GitHub.

## Setup

- **GitHub version:** one private repo holds a folder per project. Claude Code runs in GitHub Actions on my Claude plan (a token from `claude setup-token`, saved once as a secret). ChatGPT joins through Agent mode and its GitHub connector on a 30-minute schedule. A watchdog with no AI opens a GitHub issue when something is stuck.
- **Local version:** the same desk format in `~/Desks/`. macOS timers start Claude Code and Codex in turn, a folder lock keeps them from writing at once, and each turn is saved as a local git commit.

## Timeline

Times are US Mountain.

**Test 1: GitHub, Claude builds and ChatGPT reviews (Oct 10).** The task: a small help screen in [Course Quest](course-quest.md)'s demo mode, on a branch.

| Time | Event |
|---|---|
| 7:50pm | One-time setup: private desk repo, Claude token saved as a secret, ChatGPT connector access |
| 8:17pm | Claude builds the feature on a branch and checks it in the browser |
| 8:19pm | First Claude wake-up on GitHub fails: **bug 1**, a missing login setting |
| 8:25pm | ChatGPT joins and reviews: one real bug ("grows your dragon" is false on the theme without a dragon) |
| 8:26pm | ChatGPT's push should wake Claude; it doesn't: **bug 2**, the Claude action refuses push events |
| 8:45pm | ChatGPT's scheduled run passes proof of life. Claude still isn't woken: **bug 3**, the action refuses runs started by a bot |
| 8:48pm | With both fixed, ChatGPT's push wakes Claude, which fixes the wording on the branch |
| 9:15pm | ChatGPT passes review round 2 |
| 9:18pm | Claude posts `FINAL COMPLETE`. **Bug 4:** three quick ChatGPT commits started Claude twice |
| 9:45pm | ChatGPT posts `CONFIRMED COMPLETE`. Nothing was merged, deployed or opened as a pull request |

GitHub's own timer **never fired once** in that repo: six scheduled slots, about 90 minutes (**bug 5**). The watchdog opened its issue, but no email arrived (**bug 6**).

**Tests 2 and 3: the agents design the local version (Oct 11).** Claude and ChatGPT designed a no-GitHub version through the same desk: two design rounds, then a guide and two review rounds. Then a "lite" version, with Claude writing and ChatGPT reviewing hard for simplicity. Both ran without me. They found **bug 7** (a guide rewrite needed 53 agent steps against a cap of 40) and **bug 8** (the lead handed off for approval without closing the desk, so both agents kept waking). During the lite run, ChatGPT skipped four scheduled turns. With GitHub's timer dead, nothing noticed for 2½ hours (**bug 9**, still open: see below).

**Test 4: one Mac, Claude Code and Codex (Oct 11).** The task: a one-page cheat sheet. Claude drafts, Codex reviews.

| Time | Event |
|---|---|
| 9:15pm | Kit installed: four timers, a test notification arrives, secret codes posted |
| 9:25pm | False alarm: "both agents silent for 150 minutes" on a desk that's 10 minutes old (**bug 10**) |
| 9:30pm | Claude's timer fires on time, but Claude can't log in: the command-line login had expired (**bug 11**) |
| 9:39pm | Fix: a long-lived `claude setup-token` token saved in the Keychain |
| 9:45pm | **Codex wakes by itself**, answers both secret codes in 21 seconds, and waits for Claude's draft |
| 10:00pm | Claude wakes, answers both codes, writes the cheat sheet and hands it to Codex (51 seconds) |
| 10:02pm | Proof of life: **HANDS-OFF** |
| 10:15pm | Codex reviews, makes a real correction (which way of stopping a desk can be undone) and marks it done |

## Results

- **The GitHub version works end to end.** Two review rounds, a real bug caught and fixed, and a clean finish handshake, with nothing merged or deployed. The run took under two hours from "go" to confirmed done, most of it waiting on fixes.
- **The local version passed its proof of life on the first night**, once its login problem was fixed. Codex's unattended run, the biggest unknown, worked on the first try.
- **Reviews were real, not polite.** ChatGPT's review of the local guide caught that its first proof of life only proved a timer had fired, not that either AI had done anything. That became the secret-code check that both tests now rely on.
- **An outside review caught what we couldn't.** A third AI, asked to judge a GitLab version for company use, found that its security claims were stronger than its code. That version is shelved, and every guide now says plainly that this is for personal, non-confidential work.

## What broke, and what changed

| # | What broke | What changed |
|---|---|---|
| 1 | Claude's GitHub step wanted a login it wasn't given | The wake workflow passes its own token |
| 2 | The Claude action rejects push events | Pushes re-start the workflow as a manual run |
| 3 | It also rejects runs started by a bot | The Actions bot is allowed explicitly |
| 4 | A burst of commits woke Claude twice | Pushes wait 30 seconds and keep only the last of a burst |
| 5 | GitHub's timer never fired | **The partner's heartbeat is the clock:** each push checks whether Claude is due, and runs the watchdog |
| 6 | Watchdog issues didn't email me | Setup now includes "watch the repo for issues" |
| 7 | A long run hit the step cap | Cap raised to 80 |
| 8 | Handing off for approval left the desk open | Agents finish the handshake and put the approval request in the report |
| 9 | When the partner goes quiet, nothing else ticks | **Open.** I ruled out outside timer services; a backup clock on the Mac only works while it's on |
| 10 | The local watchdog called brand-new agents "silent" | New agents are timed from when the desk was created |
| 11 | The command-line Claude login expired | A long-lived token in the Keychain; a failed turn is retried instead of counted as done |

Smaller fixes along the way: the lead sets up the desk before building, never checks secrets, and never opens pull requests (hosts build paid previews for them). The start message names your repos, so safety checks know the pushes are expected, and the one-message start uses standing defaults so "go" is enough.

## Update: a test on a managed work Mac (Oct 12)

I tried local mode on a managed work Mac, with no Homebrew or Node and no admin rights:

- **Installing without admin worked**, using Node from nodejs.org unpacked into my home folder. The guide had said Homebrew, which needs an admin password; it now has a no-admin path.
- **I stopped before setup**, so this run says nothing new about the timers.
- **I found a second way that needs no Terminal at all:** the Claude and ChatGPT desktop apps' own scheduled tasks, taking turns on one shared file. Over two four-turn exercises, every turn that was set up correctly ran unattended. One review caught a real flaw, and a final check honestly said NOT DONE.
- **It wasn't hands-off.** ChatGPT reported a task as "scheduled" when it had only made a proposal. Its scheduler rejected timezones. One turn never ran, and one Claude turn stalled silently for over 30 minutes and needed me to re-time the rest.

That became [scheduled-tasks mode](../protocols/scheduled-tasks-mode.md), with the ten pitfalls listed. The lesson is the same as before: **"scheduled" isn't proof; check the run history.**

## What I took away

- **Every bug was in the plumbing.** The agents' work (code, reviews, guides) was fine every time. Logins, triggers and timers broke. Test those first, while watching.
- **Don't trust a timer you don't control.** GitHub's schedule never fired. ChatGPT's schedule worked all night, until it skipped four turns. The fix that worked was letting each agent's activity wake the other.
- **Make "it worked" impossible to fake.** A timer firing proves nothing. An agent copying a secret code it could only see by actually running proves it did its turn.
- **Label the scope honestly.** The fastest way to lose trust is a security claim the code doesn't keep.
