# Connector Contracts

Connectors turn external work-platform records into the same evidence shape used by local git collection.

Connectors should output JSON records with this minimum shape:

```json
{
  "source": "feishu",
  "type": "task_row",
  "title": "Short title",
  "date": "2026-07-01",
  "author_or_owner": "User Name",
  "author_match": true,
  "status": "unknown",
  "url": "https://...",
  "summary": "Human-readable summary",
  "confidence": "medium",
  "raw_ref": "table row id or external id"
}
```

Rules:

- Do not store secrets or raw private content by default.
- Mark inaccessible sources explicitly.
- Use identity mapping before including records in a user report.
- External evidence supplements local evidence; it does not replace it.

