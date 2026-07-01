# daily-work-report

`daily-work-report` is a Codex skill for generating trustworthy daily work reports from real evidence: local git activity, merge requests / pull requests, optional work-platform records, identity mapping, and user-defined templates.

It is designed as a personal recap assistant, not a surveillance tool.

## What It Does

- Scans local git repositories for same-day commits, branches, MR/PR refs, merge status, and dirty worktree changes.
- Separates evidence states such as local-only work, pushed branches, open MR/PR, merged work, deployed work, and verified work.
- Lets users provide their own daily-report template and style.
- Converts technical evidence into leadership-readable value summaries.
- Saves optional evidence ledgers so users can see why the report was written that way.

## Quick Start

From any workspace:

```bash
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py --roots . --output .daily-report/evidence/today-git.json
python3 ~/.codex/skills/daily-work-report/scripts/render_report.py .daily-report/evidence/today-git.json
```

With a specific date:

```bash
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py --roots . --date 2026-07-01 --output .daily-report/evidence/2026-07-01-git.json
python3 ~/.codex/skills/daily-work-report/scripts/render_report.py .daily-report/evidence/2026-07-01-git.json --date 2026-07-01
```

## Scheduled Use

You can run this skill from a local scheduler at the end of each workday.

Recommended behavior:

- run around 21:50 local time,
- scan configured repositories,
- supplement with configured external sources,
- write evidence to `.daily-report/evidence/`,
- generate a draft report,
- do not auto-send or auto-post unless you explicitly configure that.

Example shell flow:

```bash
mkdir -p .daily-report/evidence .daily-report/outputs
DAY="$(date +%F)"
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py \
  --roots . \
  --date "$DAY" \
  --output ".daily-report/evidence/$DAY-git.json"
python3 ~/.codex/skills/daily-work-report/scripts/render_report.py \
  ".daily-report/evidence/$DAY-git.json" \
  --date "$DAY" \
  > ".daily-report/outputs/$DAY.md"
```

## Configuration

Copy `config.example.json` to one of:

```text
.daily-report/config.json
~/.daily-work-report/config.json
```

Configure:

- your identity across tools
- repo roots to scan
- external evidence links
- default report style
- product naming rules

## Evidence State Rules

The skill must not overclaim. It distinguishes:

- `local_dirty`: uncommitted changes exist.
- `local_commit`: committed locally.
- `pushed_branch`: branch exists on remote.
- `mr_open`: MR/PR ref or API/page evidence exists.
- `merged`: branch/MR is merged into target branch.
- `deployed`: deployment evidence exists.
- `verified`: runtime/user-flow evidence exists.
- `unknown`: evidence is insufficient.

## Template Philosophy

Templates are semantic preferences, not string substitution only. A template can define:

- title format
- heading style
- section count flexibility
- numbered vs paragraph points
- whether to include MR details
- tomorrow-plan style
- leadership vs personal-review tone

## Privacy

Default behavior is local-first:

- no code upload
- no external API calls unless configured
- no guessing inaccessible private pages
- no team surveillance framing

## Open-Source Roadmap

- GitLab/GitHub API connector implementations.
- Feishu/Lark table extraction connector.
- Jira/Linear assignee activity connector.
- More evaluation cases.
- Template inference tests.
- Scheduler recipes for cron, launchd, systemd timers, and Codex App automations.
