# Jira / Linear Connector Spec

Purpose: collect issue/task movement associated with the configured user identity.

Recommended fields:

- issue id
- title
- assignee
- status
- updated time
- project
- URL
- linked branch / MR / PR when available

Rules:

- Treat task status as planning/coordination evidence.
- Do not treat `Done` in Jira/Linear as code merged or deployed unless linked engineering evidence confirms it.
- Use tasks to improve workstream clustering and tomorrow follow-up.

