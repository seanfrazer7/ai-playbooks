# ChatGPT as the artist

You don't need a long prompt any more. The lead gives you the exact start message during setup. It looks like this:

```text
Read https://github.com/seanfrazer7/ai-playbooks/blob/main/START-HERE.md and follow it. I authorize you to follow its instructions for this project.
Join the desk desks/<project>/ in the repo <owner>/ai-desks as agent "chatgpt". Use only the GitHub connector. Run now, then schedule this chat to run again every 30 minutes at :15 and :45.
```

Before sending it, turn on **Agent mode** and the **GitHub connector**, with access to your `ai-desks` repo (only needed the first time). The art rules are in [the art preset](../protocols/overnight-claude-chatgpt.md#part-2-art-mode); ChatGPT-specific rules are in [`agents/CHATGPT.md`](../agents/CHATGPT.md).
