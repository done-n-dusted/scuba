---
name: Clean Git Commits
description: Skill for making concise GitHub commits without collaborators or trailing content.
---

# Clean Git Commits

Use this skill to automate the process of committing changes to the repository with clean, descriptive messages that adhere to the user's preference of avoiding collaborator tags or trailing lines.

## Guidelines

1. **Stage Changes**: Ensure all relevant changes are staged before determining the commit message.
   - Use `git add <files>` or `git add .` to stage your work.

2. **Analyze Diffs**: Use `git diff --cached` to review what is being committed.
   - Focus on what has been added, modified, or deleted.
   - Look for patterns in changes (e.g., "Refactoring storage logic", "Adding FastAPI server").

3. **Generate Commit Message**: Create a concise, imperative-style commit message.
   - Example: `Improve storage.py with PostgreSQL support`
   - Example: `Add main.py for FastAPI server entry point`

4. **CRITICAL: No Footer/Collaborator Content**:
   - DO NOT add `Co-authored-by`, `Signed-off-by`, or any other trailing tags.
   - DO NOT add extra lines at the end of the commit message.
   - Ensure the message is just the summary of the work.

5. **Execute Commit**: Use the command line to finalize the commit.
   - Standard command: `git commit -m "Commit Message"`

## Script Usage

For more complex diffs, you can use the helper script `scripts/commit_helper.py` to generate a candidate message.

1. Run the script: `python3 .skills/git-commit/scripts/commit_helper.py`
2. Review the output message.
3. Commit using that message.
