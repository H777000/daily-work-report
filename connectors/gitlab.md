# GitLab Connector Spec

Purpose: collect merge requests, branch status, approvals, pipeline state, and merge status for the configured user identity.

Recommended API data:

- MR id / iid
- title
- source branch
- target branch
- author
- assignees
- created / updated / merged time
- state
- web URL
- head SHA
- pipeline status

Status mapping:

- open MR -> `mr_open`
- merged MR -> `merged`
- branch pushed without MR -> `pushed_branch`
- pipeline pass/fail -> evidence note, not deployment proof

Do not treat a passing pipeline as production deployment or user-flow verification.

