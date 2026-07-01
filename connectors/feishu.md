# Feishu / Lark Connector Spec

Purpose: collect same-day rows, task records, wiki table entries, or handoff notes associated with the configured user identity.

Recommended fields:

- `date`
- `title`
- `owner` or `assignee`
- `status`
- `link`
- `description` or `summary`
- `product` or `project`

Privacy rules:

- Use user-authorized access only.
- If login or permission blocks access, return an inaccessible-source evidence item.
- Do not guess table contents from memory.
- Prefer row metadata and summaries over raw private conversation text.

For personal installations, users can configure a Feishu table and an identity field so same-day rows for their own name supplement local git evidence.
