#!/usr/bin/env python3
"""Render a lightweight Chinese daily report from git evidence JSON.

This renderer is deliberately simple. Codex should still apply judgment,
external evidence, and user templates when available. The script provides a
portable baseline for open-source users and tests.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


KEYWORD_GROUPS = [
    (("aippt", "ai-ppt", "ppt"), "Qinyan AiPPT 生成与导出可靠性推进"),
    (("image-editor", "imageeditor", "image editor", "图像", "图片"), "Qinyan ImageEditor 稳定性优化"),
    (("translate", "translation", "翻译"), "Qinyan Translate 链路与体验优化"),
    (("chatpdf", "pdf"), "Qinyan ChatPDF / PDF 链路优化"),
    (("qindian", "point", "token", "积分", "沁点"), "Qindian 积分与记录体验优化"),
    (("sidebar", "shell", "navigation", "nav", "侧边栏", "导航"), "Qinyan 全局导航体验优化"),
]


def display_date(day: str) -> str:
    try:
        parsed = dt.date.fromisoformat(day)
        return f"{parsed.month}.{parsed.day}"
    except ValueError:
        return day


def text_blob(item: dict[str, Any]) -> str:
    parts = [
        str(item.get("name", "")),
        str(item.get("subject", "")),
        str(item.get("refs", "")),
        str(item.get("title", "")),
    ]
    return " ".join(parts).lower()


def group_name(item: dict[str, Any]) -> str:
    blob = text_blob(item)
    for keywords, name in KEYWORD_GROUPS:
        if any(keyword.lower() in blob for keyword in keywords):
            return name
    return "其他工作推进"


def status_label(item: dict[str, Any]) -> str:
    status = item.get("status") or item.get("merge_state") or "unknown"
    mr_refs = item.get("mr_refs") or []
    if item.get("merge_state") == "merged" or status == "merged":
        return "已合并"
    if mr_refs or status == "mr_open":
        return "已提 MR"
    if str(item.get("name", "")).startswith("origin/") or status == "pushed_branch":
        return "已推分支"
    if status == "local_dirty":
        return "本地进行中"
    if status == "local_commit":
        return "本地已提交"
    return "待确认"


def action_phrase(item: dict[str, Any]) -> str:
    subject = str(item.get("subject") or item.get("summary") or "").strip()
    name = str(item.get("name") or item.get("ref") or "").strip()
    label = status_label(item)
    if subject:
        return f"{label}：{subject}"
    if name:
        return f"{label}：{name}"
    return f"{label}：推进相关工作"


def collect_items(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for repo in evidence.get("repositories", []):
        branches = repo.get("branches", [])
        local_branch_names = {
            branch.get("name")
            for branch in branches
            if branch.get("name") and not str(branch.get("name")).startswith("origin/")
        }
        for branch in repo.get("branches", []):
            name = str(branch.get("name", ""))
            if name.startswith("origin/"):
                # Remote refs are often other people's work fetched into the
                # repo. Use them as status evidence only when a same-named
                # local branch is present; otherwise keep them out of the
                # user's default report.
                local_name = name.removeprefix("origin/")
                if local_name not in local_branch_names:
                    continue
                if local_name in local_branch_names:
                    continue
            items.append({**branch, "repo": repo.get("path")})
        current = repo.get("current", {})
        if current.get("dirty"):
            items.append(
                {
                    "name": current.get("branch", "current worktree"),
                    "subject": "当前工作区存在未提交改动",
                    "status": "local_dirty",
                    "repo": repo.get("path"),
                }
            )
        for worktree in repo.get("worktrees", []):
            wt_status = worktree.get("status", {})
            if not wt_status.get("dirty"):
                continue
            items.append(
                {
                    "name": worktree.get("branch") or wt_status.get("branch") or worktree.get("path"),
                    "subject": "worktree 存在未提交改动",
                    "status": "local_dirty",
                    "repo": worktree.get("path") or repo.get("path"),
                }
            )
    return items


def render_sections(items: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[group_name(item)].append(item)

    if not grouped:
        return "**一. 今日暂无可确认的本地工程变更**\n1. 本次证据中没有发现当天相关分支、提交或工作区改动。"

    ordered = sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)
    section_texts: list[str] = []
    numerals = ["一", "二", "三", "四", "五", "六"]
    for idx, (name, group_items) in enumerate(ordered[:5]):
        heading = f"**{numerals[idx]}. {name}**"
        seen: set[str] = set()
        points: list[str] = []
        for item in group_items:
            phrase = action_phrase(item)
            if phrase in seen:
                continue
            seen.add(phrase)
            points.append(phrase)
            if len(points) >= 3:
                break
        body = "\n".join(f"{i + 1}. {point}" for i, point in enumerate(points))
        section_texts.append(f"{heading}\n{body}")
    return "\n\n".join(section_texts)


def render_tomorrow(items: list[dict[str, Any]]) -> str:
    groups = []
    for item in items:
        name = group_name(item)
        if name not in groups:
            groups.append(name)
    if not groups:
        return "1. 继续补充当天工作证据，再生成正式日报。"
    points = [f"跟进 {name} 的 MR / 验收 / 上线状态。" for name in groups[:3]]
    return "\n".join(f"{i + 1}. {point}" for i, point in enumerate(points))


def evidence_summary(evidence: dict[str, Any], items: list[dict[str, Any]]) -> str:
    repos = evidence.get("repo_count", len(evidence.get("repositories", [])))
    dirty = sum(1 for item in items if item.get("status") == "local_dirty")
    mr_items = sum(1 for item in items if item.get("mr_refs"))
    return f"- 扫描仓库：{repos}\n- 识别工作项：{len(items)}\n- MR 相关项：{mr_items}\n- 本地未提交项：{dirty}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a daily report from evidence JSON.")
    parser.add_argument("evidence_json", help="Path to evidence JSON from collect_git.py.")
    parser.add_argument("--date", help="Override report date.")
    parser.add_argument("--template", help="Optional template path with {display_date}, {sections}, {tomorrow_plan}, {evidence_summary}.")
    parser.add_argument("--include-evidence", action="store_true", help="Append evidence summary.")
    args = parser.parse_args()

    evidence = json.loads(Path(args.evidence_json).read_text(encoding="utf-8"))
    day = args.date or evidence.get("date") or dt.date.today().isoformat()
    items = collect_items(evidence)
    sections = render_sections(items)
    tomorrow = render_tomorrow(items)
    summary = evidence_summary(evidence, items)

    if args.template:
        template = Path(args.template).read_text(encoding="utf-8")
    else:
        template = "**{display_date}**\n\n{sections}\n\n**明日工作计划：**\n{tomorrow_plan}\n"

    report = template.format(
        display_date=display_date(day),
        sections=sections,
        tomorrow_plan=tomorrow,
        evidence_summary=summary,
    )
    if args.include_evidence and "{evidence_summary}" not in template:
        report = f"{report.rstrip()}\n\n**证据摘要：**\n{summary}\n"
    print(report.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
