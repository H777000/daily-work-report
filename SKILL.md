---
name: daily-work-report
description: Generate trustworthy daily work reports from local git evidence, optional work-platform evidence, identity mapping, and user-defined templates. Use when the user asks for a daily report, today's branches/MRs, work summary, leadership update, personal review, or wants a reusable report workflow.
triggers:
  - daily-work-report
  - 日报
  - 今日日报
  - 工作汇报
  - 今天做了哪些分支
  - 今天做了哪些 MR
  - 总结今天工作
  - 生成今天日报
  - 扫描今天工作
argument-hint: "[date-or-template-or-empty]"
---

# Daily Work Report

## Purpose

Turn real work evidence into a concise, trustworthy daily report in the user's preferred style.

This skill is a personal work recap assistant, not an employee-monitoring tool. It should help the user explain their own work from evidence they can inspect and correct.

## Product Principle

The report is only the final surface. The product-quality workflow is:

```text
Evidence collection
-> identity filtering
-> status classification
-> workstream clustering
-> value translation
-> template rendering
-> evidence-gap disclosure
```

Do not write a confident report from memory alone when current evidence is available.

## When To Activate

Use this skill when the user asks:

- "总结今天日报"
- "今天做了哪些分支 / MR"
- "全面扫描本地当日工作"
- "按这个模板写日报"
- "生成工作汇报"
- "给领导发一个简短汇报"
- "复盘今天做了什么"

Also use it when the user provides a daily-report template and wants future reports to follow it.

Do not use it for unrelated writing, one-off text polishing without evidence gathering, or formal legal/HR monitoring reports.

## Default Output Contract

Unless the user provides another template:

- Use a date-only title, such as `**7.1**`.
- Use bold section headings.
- Let section count vary with the day's real workstreams. Do not force 3 or 4 sections.
- Each section usually has 1-3 numbered points. Do not pad.
- `明日工作计划` uses numbered points, but count varies with the real next steps.
- Order by product/business value, not by commit time.
- For product-family features, prefix with the product when useful, for example `Qinyan Translate`, `Qinyan AiPPT`, `Qinyan ImageEditor`.
- Keep it concise and leadership-readable. Do not dump branch names unless the user asks.

## Evidence Sources

### Required First Source: Local Git

Inspect local repositories before writing:

1. Current repo status and dirty diff.
2. Same-day commits.
3. Same-day local branches.
4. Remote branches pushed today.
5. MR/PR refs when available.
6. Whether branch heads are merged into the target branch.
7. Uncommitted work that should be described as local progress, not shipped work.

Use the helper when possible:

```bash
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py --roots . --date YYYY-MM-DD --output .daily-report/evidence/YYYY-MM-DD-git.json
```

If the helper is unavailable, use equivalent git commands:

```bash
git status --short --branch
git branch --format='%(committerdate:iso8601)|%(refname:short)|%(objectname:short)|%(subject)' --sort=-committerdate
git log --all --since='YYYY-MM-DD 00:00 +0800' --date=iso --pretty=format:'%h|%ad|%D|%s'
git reflog --date=iso --all --since='YYYY-MM-DD 00:00 +0800' --format='%gd|%cd|%gs'
git fetch origin '+refs/merge-requests/*/head:refs/remotes/origin/merge-requests/*' --prune
```

### Optional External Sources

Use external evidence only when configured, accessible, and relevant:

- Feishu/Lark wiki tables, docs, task boards, or messages.
- GitLab/GitHub MRs and PRs.
- Jira, Linear, Notion, Slack, email, calendars.

External sources supplement local evidence. They do not replace it.

If a page is inaccessible because of login, permissions, or browser state, say so briefly and continue from available evidence. Never invent inaccessible content.

### Configured Feishu/Lark Supplement Rule

When local config defines Feishu/Lark sources and identity names, check same-day rows or records for the configured identity after local git scanning.

Use those rows only if they materially change the value summary, MR list, or tomorrow follow-up. Keep private wiki/table URLs in local config files, not in public skill files.

## Identity Mapping

Before including work, map "the user" across systems:

```text
display name
git author names
git author emails
GitHub/GitLab usernames
Feishu/Lark member names
Jira/Linear assignees
```

When no identity config exists, report the limitation and rely on local branch/worktree evidence rather than all team activity.

Never silently include other people's work as the user's work.

## Status Vocabulary

Use precise status language:

- `local_dirty`: uncommitted local work.
- `local_commit`: committed locally.
- `pushed_branch`: pushed branch exists.
- `mr_open`: MR/PR evidence exists.
- `merged`: branch/MR is merged into target branch.
- `deployed`: deployment evidence exists.
- `verified`: runtime/user-flow evidence exists.
- `unknown`: evidence is insufficient.

Do not say `上线`, `已提 MR`, `已合并`, or `已验证` unless evidence supports that exact state.

## Workstream Clustering

Cluster evidence into user-facing workstreams:

Good:

```text
Qinyan AiPPT 长任务生成与导出可靠性提升
Qinyan Translate 登录链路与落地页体验修复
Qinyan ImageEditor 长任务稳定性优化
```

Bad:

```text
Modified 23 files
Commit d0c78408a
Updated auth_center_client.py
```

Translate technical activity into business value:

```text
state machine -> lowers long-task interruption risk
MR split -> lowers review and rollback risk
login fallback -> improves local validation speed
telemetry contract -> improves data trust for product decisions
```

## Template Handling

If the user provides a template, follow the template over defaults.

Learn these rules from the template:

- Title shape.
- Whether headings are bold.
- Section count flexibility.
- Numbered vs paragraph bullets.
- Whether MR/branch details appear.
- How tomorrow plans are written.
- Tone: leadership report, personal review, standup, weekly rollup, or delivery note.

Use templates semantically. Do not merely replace words.

If the template conflicts with evidence safety, evidence safety wins. Example: if the template says "已上线" but evidence only shows a pushed branch, write "已推分支，待上线确认".

## Workflow

1. Determine date and timezone. Default to current local date.
2. Load any local config from `.daily-report/config.json` or `~/.daily-work-report/config.json` if present.
3. Collect local git evidence from the current repo and configured roots.
4. Collect optional external evidence if configured and accessible.
5. Filter by identity.
6. Classify status for each work item.
7. Cluster work items into 2-5 value-oriented streams as appropriate.
8. Render using the user's provided template, saved template, or default template.
9. Include a short evidence note only when useful or when the user asks for branches/MRs.
10. Mention evidence gaps and inaccessible sources briefly.

## Recommended Skill Package Files

```text
daily-work-report/
  SKILL.md
  README.md
  config.example.json
  scripts/
    collect_git.py
    render_report.py
  templates/
    leadership_zh.md
    personal_review_zh.md
  connectors/
    README.md
    feishu.md
    gitlab.md
    github.md
    jira-linear.md
  evals/
    README.md
    cases/
```

## Guardrails

- Do not fabricate inaccessible Feishu/GitLab/GitHub/Jira content.
- Do not upload source code, private docs, or internal links to third-party services by default.
- Do not expose secrets, tokens, private customer content, or raw internal discussions.
- Do not turn this into employee surveillance. Use personal identity mapping and user-authorized sources only.
- Do not count unrelated dirty files as delivered work.
- Do not confuse local evidence with production readiness.

## Verification

Before finalizing a daily report, check:

- At least one current evidence source was inspected.
- Local dirty work is separated from merged/MR-backed work.
- MR/PR status claims are backed by refs, API, or visible page evidence.
- External-source failures are disclosed instead of guessed.
- The final report matches the user's template or stated preferences.
- The report is concise enough for the target audience.

## Open-Source Quality Bar

For public release, keep this skill:

- Dependency-light: scripts use Python standard library by default.
- Portable: works across macOS/Linux and new machines.
- Configurable: identity, roots, sources, and templates are user-editable.
- Auditable: evidence JSON can be saved and reviewed.
- Extensible: connectors are documented contracts, not hardcoded to one company.
