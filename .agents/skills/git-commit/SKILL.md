---
name: git-commit
description: A set of procedures to follow whenever committing code, ensuring the README.md is always kept up-to-date.
---

# Git Commit Skill

This skill defines the workflow you MUST follow right before committing changes using git.

## Instructions

Whenever you are asked to make a commit or are preparing to run `git commit`, perform the following steps:

1. **Assess Code Modifications**: Review the scope of the changes you've just made.
2. **Verify README Accuracy**: Determine if any of the following happened during your work:
   - Added new application features or CLI commands.
   - Introduced a new HTTP endpoint (API).
   - Changed the project or folder structure (e.g. added a new module).
   - Modified the installation/setup process or added new dependencies.
3. **Update README.md**: If any of these changes occurred, you **MUST** modify `README.md` to document the new state of the project *before* making the commit.
4. **Stage and Commit**: Once the `README.md` is fully up-to-date, add it to your staged files alongside your code updates, and create your commit with a descriptive message (e.g., `git add . && git commit -m "Your descriptive message"`).

By diligently following this skill, our central documentation will never fall out of sync with the underlying codebase!
