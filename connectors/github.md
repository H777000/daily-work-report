# GitHub Connector Spec

Purpose: collect pull requests, branch status, checks, and merge state for configured users.

Recommended API data:

- PR number
- title
- head branch
- base branch
- author
- assignees/reviewers
- state
- merged timestamp
- URL
- check suite conclusion

Status mapping:

- open PR -> `mr_open`
- merged PR -> `merged`
- pushed branch without PR -> `pushed_branch`
- check suite pass/fail -> evidence note, not production proof

