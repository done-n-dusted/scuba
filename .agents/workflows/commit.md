---
description: How to commit code while adhering to the git-commit skill
---

This workflow enforces the `git-commit` skill, ensuring commits are made with the correct author identity and that the README documentation is kept in sync with code changes.

1. **Set Git Identity**: 
Set the expected git configuration to prevent identity mismatches.
// turbo
`git config user.name "done-n-dusted"`
// turbo
`git config user.email "31320.anurag@gmail.com"`

2. **Assess Code Modifications**: 
Review the scope of the changes you have just made.
`git status`
`git diff`

3. **Verify README Accuracy**: 
Determine if any of the following happened during your work:
- Added new application features or CLI commands.
- Introduced a new HTTP endpoint (API).
- Changed the project or folder structure (e.g., added a new module).
- Modified the installation/setup process or added new dependencies.

4. **Update README.md**: 
If any of the changes described in step 3 occurred, you MUST modify `README.md` to document the project's new state *before* proceeding.

5. **Stage and Commit**: 
Once the `README.md` is updated and accurate, stage all changes and commit with a descriptive message.
`git add .`
`git commit -m "[Your descriptive message]"`
