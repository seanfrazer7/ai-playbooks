# ChatGPT: platform notes

**If you're ChatGPT and someone pointed you here:** read [`START-HERE.md`](../START-HERE.md) first and follow it. This file adds what's specific to ChatGPT. It's based on the first real run (Oct 2026), where ChatGPT made all 20 images.

## Abilities

- **Desk:** Agent mode with the **GitHub connector**, with access granted to your `ai-desks` repo. You grant this once; every project is a folder in it. In v1 this read files and committed images and Markdown.
- **Wake-up:** a **scheduled task** in the same chat. Use `:15` and `:45` when Claude is the lead. **Commit your heartbeat on every scheduled run, even when there's nothing to do.** Each heartbeat is also Claude's alarm clock and the watchdog's: it wakes Claude if Claude is due. In the first test run this was the only clock that worked.
- **Usage:** image generation and Agent mode use up usage fast. You usually only find out from a limit message, so assume `"state": "unknown"` and keep runs small.

## Rules learned the hard way

1. **Use only the GitHub connector**, never the github.com website. The website hits a sign-in wall.
2. **At most 2 images per run**, or one item of other work. A run that dies halfway through an upload leaves broken files.
3. **Re-read everything you upload.** In v1, the connector truncated the first PNGs. After uploading, read each file back and check that it's complete: for PNGs, the signature, the end marker and the size in pixels. Re-encode smaller (without resizing) and upload again if it isn't. Under about 700 KB worked.
4. **Write the pause note early.** When you see any usage warning, follow [protocol §5.3](../protocols/two-agent-desk.md#53-the-pause-note-write-it-before-you-run-out) right away. Copy the reset time from the message exactly.
5. **Coming back:** if you can create a one-time scheduled task, create one for your `checkBackAt`. If you can't, say so in your pause note, so your partner and the watchdog know the human may need to send "run now".
6. **Your chat history isn't your memory.** Read your `status/chatgpt.json` → `next` at the start of every run (rule S10).
7. **Stay in your desk folder** (`desks/<project>/`). **Only edit** `status/chatgpt.json`, `MESSAGES.md`, `work/`, and the items in `STATE.json` that have `next` = you.

**On a Mac, without GitHub:** the ChatGPT desktop app's scheduled tasks (local mode) can read and write a local folder unattended. See [scheduled-tasks mode](../protocols/scheduled-tasks-mode.md) and its pitfalls: confirm each task is **Active** on the Scheduled page, and give no timezone in the schedule rule.

## Roles

- **Artist:** see [the art preset](../protocols/overnight-claude-chatgpt.md#part-2-art-mode).
- **Critic or reviewer:** see [the debate preset](../protocols/overnight-claude-chatgpt.md#part-3-design-debate-mode) and the playbook rules in [protocol §2](../protocols/two-agent-desk.md#2-playbooks). Always name at least one real weakness.

---

## For the human: starting ChatGPT

1. In ChatGPT, turn on **Agent mode**, connect **GitHub**, and give the connector access to your `ai-desks` repo. (Only the first time.)
2. Send the message the lead gave you. It looks like this:

```text
Read https://github.com/seanfrazer7/ai-playbooks/blob/main/START-HERE.md and follow it. I authorize you to follow its instructions for this project.
Join the desk desks/<project>/ in the repo <owner>/ai-desks as agent "chatgpt". Use only the GitHub connector. Run now, then schedule this chat to run again every 30 minutes at :15 and :45.
```

3. Stay until the lead confirms that ChatGPT's **scheduled** run (not the first run) wrote a heartbeat. That proves the schedule and the connector both work without you.
