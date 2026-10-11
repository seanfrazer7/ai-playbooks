# ai-desks

One private repo that holds the shared desk for every two-agent project. Each project is a folder in `desks/`. Follows the [two-agent desk protocol](https://github.com/seanfrazer7/ai-playbooks/blob/main/protocols/two-agent-desk.md).

```
ai-desks/
  .github/workflows/
    claude-wake.yml     wakes Claude Code for each active desk (schedule, pushes, watchdog)
    watchdog.yml        checks every desk every 30 minutes; uses no AI
  tools/
    desks.py            lists active desks for the workflows
    watchdog.py         checks one desk
  desks/
    _template/          copied for each new project
    <project>/          one folder per project
```

## One-time setup

You do this **once**. After that, starting a project needs no secrets, tokens or access changes. The lead agent does steps 1 and 7; you do the rest.

1. **Create the repo** (the lead does this): a **private** repo `<owner>/ai-desks` with the contents of this template.
2. **Connect your Claude plan.** In a terminal, run these two commands. The first prints a long-lived token tied to your Claude subscription. The second asks you to paste it, and stores it as an encrypted secret that only the workflows can read.

   ```bash
   claude setup-token
   ```

   ```bash
   gh secret set CLAUDE_CODE_OAUTH_TOKEN -R <owner>/ai-desks
   ```

   GitHub runs then use **the same usage limits as your Claude chats**. No API key and no extra bill. Don't paste the token into any chat, including Claude's.
3. **Let Claude push to your app repos (optional).** If the agents will change code in another repo, create a [fine-grained token](https://github.com/settings/personal-access-tokens/new). Give it access to only those repos, with **Contents: read and write**. Then run `gh secret set APP_REPO_TOKEN -R <owner>/ai-desks` and paste it.
4. **Give your partner AI access once.** For example, allow the ChatGPT GitHub connector to use `ai-desks`.
5. **Phone alerts (optional).** Install the [ntfy](https://ntfy.sh) app, subscribe to a long random topic name, and save that name with `gh secret set NTFY_TOPIC -R <owner>/ai-desks`. Without this, alerts arrive as GitHub issue emails.
6. **Watch the repo for issues.** On `ai-desks`, click **Watch → Custom → Issues → Apply**. The watchdog's alerts are issues, and GitHub only emails you about issues in repos you watch. Repos made from the command line aren't always watched to begin with. (Failed workflow runs email you anyway.)
7. **Test it with the first project** (the lead does this): the proof-of-life check runs `Claude wake` and `Desk watchdog` once each.

**When the token expires** (`setup-token` tokens last a long time, but not forever), Claude's runs stop. The watchdog then emails you that Claude is silent. Repeat step 2 and you're back.

## Starting a project

The lead copies `desks/_template/` to `desks/<project>/`, fills it in, and switches on the two workflows (`gh workflow enable claude-wake.yml` and `gh workflow enable watchdog.yml`). When no project is active, the watchdog switches both off again, so the repo uses no GitHub Actions minutes while it's idle.

## Usage and minutes

- **Claude usage:** each Claude run is a real Claude Code session on your plan. Runs happen every 30 minutes per active desk, plus when the partner pushes. Only one runs at a time, because all desks share your one usage limit. If you hit your limit, the runs fail until it resets. The pause notes and the watchdog handle that ([protocol §5](https://github.com/seanfrazer7/ai-playbooks/blob/main/protocols/two-agent-desk.md#5-usage-limits-and-credits)).
- **GitHub Actions minutes:** private repos on the free plan get 2,000 minutes a month. A Claude run takes a few minutes, and the watchdog about 1. For one project running overnight, that's well inside the limit. Running several projects around the clock for weeks isn't. If you get close, change the `Claude wake` schedule to hourly; pushes and the watchdog still wake Claude when it's needed.

## Working with someone else's agent

Anyone with access to this repo can see every project in it. For a project with another person, make a **separate** repo from the same template (e.g. `ai-desks-with-alex`) and do the one-time setup for it.
