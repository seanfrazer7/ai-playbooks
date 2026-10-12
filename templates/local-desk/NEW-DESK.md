# Starting a new desk (instructions for Claude Code)

The human has asked you to start a new desk. Their message gave a goal and a work folder (a path, or "none"). Do this and nothing else:

1. Pick a short name from the goal: lowercase letters, digits and dashes only (for example `fix-login-bug`). Make sure `~/Desks/<name>` doesn't exist.
2. Run this one command, with the goal and folder filled in (leave `--folder` out if the folder is "none"). The human's message is their yes, so `--yes` is allowed here:

   `sh ~/DeskKit/setup.sh --yes --name <name> --goal "<the goal, in the human's words>" --folder "<path>"`

3. If it prints an error, tell the human what it says and stop. Don't work around it.
4. Don't edit `STATE.json` or any other file by hand. The command made them.
5. Tell the human in three lines: the desk name and path; that Claude and Codex will wake on their own timers (Claude at :00 and :30, Codex at :15 and :45), so nothing needs starting; and, if they gave a work folder, that changes will appear only on the branch `desk/<name>` there and nothing is pushed.
6. If this is the first desk on this Mac, remind them to do the proof of life (section 6 of protocols/local-mode.md in ai-playbooks).
