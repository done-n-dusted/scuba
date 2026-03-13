---
description: Create a pull request while adhering to the git-commit skill standards
---

This workflow ensures that the `git-commit` skill is followed before creating a pull request.

1. **Adhere to git-commit skill**:
   - Verify Git identity (name should be `"done-n-dusted"`).
   - Review code modifications.
   - Verify `README.md` accuracy and update if necessary (new features, endpoints, structure changes, or dependencies).
   - Stage and commit with a descriptive message.

2. **Branch Management**:
   - Ensure you are on a feature branch, not `main`. If on `main`, create a new branch: `git checkout -b <branch-name>`.

3. **Push Changes**:
   - Push the branch to the remote: `git push origin <branch-name>`.

4. **Create Pull Request**:
   - Use the `gh` CLI if available to create the PR: `gh pr create --title "<title>" --body "<body>"`.
   - If `gh` is not available, provide the user with the link to create the PR manually on the web interface.

5. **Final Check**:
   - Confirm that the PR includes the updated `README.md` and follows all project engineering standards.
