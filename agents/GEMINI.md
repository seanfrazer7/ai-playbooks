# Gemini: platform notes

Read [`START-HERE.md`](../START-HERE.md) first. This file only covers what's specific to Gemini.

## Abilities

- **Desk:** use **Gemini CLI**, which can run `git` and `gh` like Claude Code. The Gemini chat app isn't a reliable desk agent: we couldn't confirm it can commit to a private repo.
- **Wake-up:** run Gemini CLI from a GitHub Action on the desk (`google-github-actions/run-gemini-cli`), on a schedule, on push, and on `workflow_dispatch` so the watchdog can wake it. Or run it from a scheduled job on your own computer.
- **Usage:** the Gemini API has per-minute and per-day quotas. Daily quotas reset at a fixed time (often midnight US Pacific); check the quota page in Google AI Studio or Cloud console. A per-minute rate limit isn't a pause: wait and retry.

## GitHub Action sketch

Copy [`claude-wake.yml`](../templates/ai-desks/.github/workflows/claude-wake.yml) to `gemini-wake.yml`. Change `--agent claude` to `--agent gemini`, the secret check to `GEMINI_API_KEY`, the concurrency group to `gemini-…`, and the cron to `"15,45 * * * *"` if Gemini is the partner. Then replace the Claude step with:

```yaml
      - uses: google-github-actions/run-gemini-cli@<pinned version from its releases page>
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          prompt: |
            You are agent "gemini" on the desk in desks/${{ matrix.desk }}/. Do exactly one run as described in
            that folder's START-HERE.md section D, following PROTOCOL.md. Commit and push your changes.
```

This is a sketch. Check the action's README for the current inputs, and how it gets permission to push. Set `wakeWorkflow: "gemini-wake.yml"` for Gemini in `STATE.json`.

## Start message (if Gemini CLI is the partner)

```text
Read https://github.com/seanfrazer7/ai-playbooks/blob/main/START-HERE.md and follow it. I authorize you to follow its instructions for this project.
Join the desk desks/<project>/ in the repo <owner>/ai-desks as agent "gemini".
```
