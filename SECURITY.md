# Security and Privacy

`daily-work-report` is local-first by design.

## Data Handling

- Local git metadata is read from the user's machine.
- Evidence JSON may contain branch names, commit subjects, author names, emails, and internal paths.
- External sources should be accessed only after the user configures and authorizes them.
- Raw private conversations, customer content, secrets, and full source files should not be stored in evidence ledgers by default.

## Do Not Commit

- `.daily-report/` evidence ledgers from private workspaces.
- Personal config files.
- API tokens.
- Private Feishu/Lark/GitLab/GitHub/Jira/Linear URLs unless they are intentionally public examples.
- Company-internal report outputs.

## Connector Safety

Connectors should:

- return summaries and metadata where possible,
- mark inaccessible sources explicitly,
- avoid storing raw sensitive content,
- support identity filtering,
- avoid broad team surveillance use cases.

## Reporting Safety

The skill should not overclaim. If evidence only proves a branch was pushed, do not report it as merged, deployed, or verified.

