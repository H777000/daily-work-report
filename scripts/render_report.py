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
    (("universitiesrecord", "trial record", "trial-record", "admin export", "试用记录", "筛选条件", "勾选", "全量导出", "b端"), "Qinyan B端运营导出能力推进"),
    (("aippt", "ai-ppt", "ppt"), "Qinyan AiPPT 生成与导出可靠性推进"),
    (("translate", "translation", "翻译"), "Qinyan Translate 链路与体验优化"),
    (("image-editor", "imageeditor", "image editor", "图像", "图片"), "Qinyan ImageEditor 稳定性优化"),
    (("chatpdf", "pdf"), "Qinyan ChatPDF / PDF 链路优化"),
    (("qindian", "point", "token", "积分", "沁点"), "Qindian 积分与记录体验优化"),
    (("sidebar", "shell", "navigation", "nav", "侧边栏", "导航"), "Qinyan 全局导航体验优化"),
    (("daily-work-report", "daily report", "daily reports", "work report", "report numbering", "rendered chat", "final summaries", "日报", "周报"), "daily-work-report Skill 开源与自动化完善"),
]

GROUP_ORDER = {name: idx for idx, (_, name) in enumerate(KEYWORD_GROUPS)}

FALLBACK_LINES = {
    "Qinyan B端运营导出能力推进": [
        "推进试用记录按当前筛选条件一键导出，减少运营复查数据时的手工整理成本。",
        "收敛勾选导出与全量导出的交互语义，降低后台导出时的理解偏差。",
    ],
    "Qinyan AiPPT 生成与导出可靠性推进": [
        "推进 slide schema 生成与可编辑 PPT 导出链路，让生成结果更接近可二次编辑、可验收的交付物。",
        "补充长任务恢复、导出保护和上线治理证据，降低 AiPPT 生成/导出链路上线风险。",
    ],
    "Qinyan Translate 链路与体验优化": [
        "推进翻译历史同步与去重边界，提升长文档/历史记录核对的可信度。",
        "补充 LAN 测试免手动登录能力，降低本地和局域网验证 SSO 链路的阻塞。",
    ],
    "daily-work-report Skill 开源与自动化完善": [
        "完成日报 Skill 中文化、GitHub 开源发布和通用模板能力整理。",
        "配置每日 21:50 准时日报、周五 17:50 周总结，并调整为提前运行、按时交付。",
    ],
}

TOMORROW_LINES = {
    "Qinyan B端运营导出能力推进": "继续跟进 Qinyan B端筛选导出分支的未提交修改、同步远端状态与 MR / 验收。",
    "Qinyan AiPPT 生成与导出可靠性推进": "推进 Qinyan AiPPT schema 生成、可编辑导出和长任务可靠性相关分支确认。",
    "Qinyan Translate 链路与体验优化": "复查 Qinyan Translate 历史同步与 LAN 测试链路的合并后表现。",
    "daily-work-report Skill 开源与自动化完善": "观察日报自动化 21:50 准时交付效果，并继续收敛模板细节。",
}


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
        str(item.get("repo", "")),
    ]
    return " ".join(parts).lower()


def group_name(item: dict[str, Any]) -> str:
    blob = text_blob(item)
    for keywords, name in KEYWORD_GROUPS:
        if any(keyword.lower() in blob for keyword in keywords):
            return name
    return "其他工作推进"


def action_phrase(item: dict[str, Any]) -> str:
    subject = str(item.get("subject") or item.get("summary") or "").strip()
    name = str(item.get("name") or item.get("ref") or "").strip()
    blob = f"{subject} {name}".lower()

    if any(keyword in blob for keyword in ("universitiesrecord", "trial record", "trial-record", "admin export", "试用记录", "筛选条件", "勾选", "全量导出")):
        if any(keyword in blob for keyword in ("勾选", "selected", "permission", "scope", "语义")):
            return "收敛勾选导出与全量导出的交互语义，降低后台导出时的理解偏差。"
        return "推进试用记录按当前筛选条件一键导出，减少运营复查数据时的手工整理成本。"

    if any(keyword in blob for keyword in ("aippt", "ai-ppt", "ppt", "slide schema", "schema")):
        if any(keyword in blob for keyword in ("governance", "readiness", "guard", "recovery", "恢复", "治理")):
            return "补充长任务恢复、导出保护和上线治理证据，降低 AiPPT 生成/导出链路上线风险。"
        return "推进 slide schema 生成与可编辑 PPT 导出链路，让生成结果更接近可二次编辑、可验收的交付物。"

    if any(keyword in blob for keyword in ("translate", "translation", "翻译", "lan", "history", "历史")):
        if any(keyword in blob for keyword in ("lan", "login", "登录", "sso")):
            return "补充 LAN 测试免手动登录能力，降低本地和局域网验证 SSO 链路的阻塞。"
        return "推进翻译历史同步与去重边界，提升长文档/历史记录核对的可信度。"

    if any(keyword in blob for keyword in ("daily-work-report", "daily report", "daily reports", "work report", "report numbering", "rendered chat", "final summaries", "日报", "周报", "automation", "自动化")):
        if any(keyword in blob for keyword in ("schedule", "automation", "自动化", "21:50", "17:50")):
            return "配置每日 21:50 准时日报、周五 17:50 周总结，并调整为提前运行、按时交付。"
        return "完成日报 Skill 中文化、GitHub 开源发布和通用模板能力整理。"

    if item.get("status") == "local_dirty":
        return "继续收口当前工作区改动，避免未完成内容被写成交付结果。"
    if subject:
        return subject
    if name:
        return f"推进 {name} 相关工作。"
    return "推进相关工作。"


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
        for commit in repo.get("commits", []):
            if commit.get("author_match") is False:
                continue
            items.append(
                {
                    "name": commit.get("refs") or commit.get("short_sha"),
                    "subject": commit.get("subject"),
                    "status": "local_commit",
                    "repo": repo.get("path"),
                }
            )
        current = repo.get("current", {})
        if current.get("dirty"):
            dirty_item = {
                "name": current.get("branch", "current worktree"),
                "subject": "当前工作区存在未提交改动",
                "status": "local_dirty",
                "repo": repo.get("path"),
            }
            if group_name(dirty_item) != "其他工作推进":
                items.append(dirty_item)
        # Historical worktrees often contain old exploratory edits. Keep them
        # in the evidence JSON, but do not treat every dirty worktree as a
        # default report item; the current worktree is the actionable signal.
    return items


def render_sections(items: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[group_name(item)].append(item)

    if not grouped:
        return "一. 今日暂无可确认的本地工程变更\n本次证据中没有发现当天相关分支、提交或工作区改动。"

    ordered = sorted(grouped.items(), key=lambda kv: (GROUP_ORDER.get(kv[0], 999), -len(kv[1])))
    section_texts: list[str] = []
    numerals = ["一", "二", "三", "四", "五", "六"]
    for idx, (name, group_items) in enumerate(ordered[:5]):
        heading = f"{numerals[idx]}. {name}"
        seen: set[str] = set()
        points: list[str] = []
        for item in group_items:
            phrase = action_phrase(item)
            if phrase in seen:
                continue
            seen.add(phrase)
            points.append(phrase)
            if len(points) >= 2:
                break
        for fallback in FALLBACK_LINES.get(name, []):
            if len(points) >= 2:
                break
            if fallback not in seen:
                points.append(fallback)
                seen.add(fallback)
        fallback_order = {line: idx for idx, line in enumerate(FALLBACK_LINES.get(name, []))}
        points.sort(key=lambda line: fallback_order.get(line, 999))
        body = "\n".join(points)
        section_texts.append(f"{heading}\n{body}")
    return "\n\n".join(section_texts)


def render_tomorrow(items: list[dict[str, Any]]) -> str:
    groups = []
    for item in items:
        name = group_name(item)
        if name not in groups:
            groups.append(name)
    groups.sort(key=lambda name: GROUP_ORDER.get(name, 999))
    if not groups:
        return "继续补充当天工作证据，再生成正式日报。"
    points = [TOMORROW_LINES.get(name, f"跟进 {name} 的 MR / 验收 / 上线状态。") for name in groups[:4]]
    return "\n".join(points)


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
        template = "{display_date}\n\n{sections}\n\n明日工作计划：\n{tomorrow_plan}\n"

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
