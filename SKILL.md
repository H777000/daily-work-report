---
name: daily-work-report
description: 从本地 git 证据、可选工作平台证据、身份映射和用户自定义模板生成可信的中文日报/周报。适用于用户询问今日分支、MR、工作总结、领导汇报、个人复盘，或希望沉淀可复用日报工作流的场景。
triggers:
  - daily-work-report
  - 日报
  - 今日日报
  - 周报
  - 工作汇报
  - 今天做了哪些分支
  - 今天做了哪些 MR
  - 总结今天工作
  - 生成今天日报
  - 扫描今天工作
argument-hint: "[日期/模板/留空]"
---

# Daily Work Report

## 目标

把真实工作证据整理成简短、可信、符合用户个人风格的日报或周报。

这个 Skill 是个人工作复盘助手，不是员工监控工具。它帮助用户基于自己可检查、可修正的证据解释当天或本周的真实工作。

## 产品原则

日报只是最后的输出层。完整流程应该是：

```text
采集证据
-> 识别本人身份
-> 判断工作状态
-> 聚合工作主线
-> 翻译成业务价值
-> 按模板渲染
-> 说明证据缺口
```

只要可以获取当前证据，就不要只凭记忆写肯定语气的报告。

## 什么时候使用

用户说这些话时使用本 Skill：

- “总结今天日报”
- “今天做了哪些分支 / MR”
- “全面扫描本地当日工作”
- “按这个模板写日报”
- “生成工作汇报”
- “给领导发一个简短汇报”
- “复盘今天做了什么”
- “总结本周周报”

当用户提供自己的日报模板，并希望以后都按这个模板输出时，也使用本 Skill。

不要把它用于与证据无关的普通润色、一次性文案改写，或正式法律/HR 监控类报告。

## 默认输出规则

如果用户没有提供其他模板：

- 标题只写日期，例如 `**7.1**`。
- 大标题加粗。
- 大标题数量按当天真实工作主线决定，不强行固定 3 个或 4 个。
- 每个大标题下通常写 1-3 个编号小点，不为了凑数硬拆。
- `明日工作计划` 使用编号小点，但数量也按真实下一步决定。
- 按产品/业务价值排序，不按提交时间流水账排序。
- 同一产品体系下的功能默认带产品前缀，例如 `Qinyan Translate`、`Qinyan AiPPT`、`Qinyan ImageEditor`。
- 面向领导汇报时保持简短、价值优先，不堆分支名和技术细节，除非用户明确要求。

## 证据来源

### 第一优先级：本地 Git

写报告前必须先检查本地仓库：

1. 当前分支、工作区状态和未提交改动。
2. 当天或本周提交。
3. 当天或本周本地分支。
4. 推送到远端的分支。
5. 可用时检查 MR / PR refs。
6. 分支 head 是否已经进入目标分支。
7. 未提交工作只能写成本地进度，不能写成已交付成果。

优先使用辅助脚本：

```bash
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py --roots . --date YYYY-MM-DD --output .daily-report/evidence/YYYY-MM-DD-git.json
```

如果脚本不可用，可以用等价 git 命令：

```bash
git status --short --branch
git branch --format='%(committerdate:iso8601)|%(refname:short)|%(objectname:short)|%(subject)' --sort=-committerdate
git log --all --since='YYYY-MM-DD 00:00 +0800' --date=iso --pretty=format:'%h|%ad|%D|%s'
git reflog --date=iso --all --since='YYYY-MM-DD 00:00 +0800' --format='%gd|%cd|%gs'
git fetch origin '+refs/merge-requests/*/head:refs/remotes/origin/merge-requests/*' --prune
```

### 可选外部来源

只有在用户配置、授权且可访问时，才使用外部证据：

- 飞书/Lark wiki 表格、文档、任务板或消息。
- GitLab/GitHub MR 和 PR。
- Jira、Linear、Notion、Slack、邮件、日历等。

外部来源只能补充本地证据，不能替代本地证据。

如果页面因为登录、权限或浏览器状态不可访问，要简短说明并继续使用已有证据。不要编造不可访问页面的内容。

### 飞书/Lark 补充规则

当本地配置定义了飞书/Lark 来源和身份名称时，在本地 git 扫描之后，检查同日或本周属于该身份的行/记录。

只有这些记录会改变价值总结、MR 列表或明日/下周跟进项时，才纳入报告。私有 wiki/table 链接必须放在本地 config 中，不要写进公开 Skill 文件。

## 身份映射

纳入工作前，先把“用户是谁”映射到不同系统：

```text
显示名
git author name
git author email
GitHub/GitLab 用户名
飞书/Lark 成员名
Jira/Linear assignee
```

如果没有身份配置，要说明限制，并优先依赖本地分支、worktree 和当前工作区证据，而不是把团队所有活动都算成用户工作。

永远不要静默把别人的工作写成用户自己的工作。

## 状态词表

必须使用精确状态：

- `local_dirty`：本地未提交改动。
- `local_commit`：本地已提交。
- `pushed_branch`：已推分支。
- `mr_open`：有 MR/PR 证据。
- `merged`：分支/MR 已进入目标分支。
- `deployed`：有部署证据。
- `verified`：有运行时或真实流程验证证据。
- `unknown`：证据不足。

没有证据时，不要写 `上线`、`已提 MR`、`已合并` 或 `已验证`。

## 工作主线聚合

把证据聚合成用户能理解的工作主线。

好例子：

```text
Qinyan AiPPT 长任务生成与导出可靠性提升
Qinyan Translate 登录链路与落地页体验修复
Qinyan ImageEditor 长任务稳定性优化
```

坏例子：

```text
Modified 23 files
Commit d0c78408a
Updated auth_center_client.py
```

把技术动作翻译成业务价值：

```text
state machine -> 降低长任务中断后无法恢复的风险
MR split -> 降低评审和回滚风险
login fallback -> 提升本地验证效率
telemetry contract -> 提升产品数据可信度
```

## 模板处理

如果用户提供模板，优先遵循用户模板。

需要从模板中学习这些规则：

- 标题形式。
- 大标题是否加粗。
- 大标题数量是否灵活。
- 小点是编号还是自然段。
- 是否写 MR/分支细节。
- 明日计划或下周计划的写法。
- 语气是领导汇报、个人复盘、站会同步、周报还是交付说明。

模板要语义化理解，不能只做文字替换。

如果模板和证据安全冲突，证据安全优先。例如模板写“已上线”，但证据只显示已推分支，就写“已推分支，待上线确认”。

## 工作流程

1. 确定日期和时区，默认使用当前本地日期。
2. 如存在 `.daily-report/config.json` 或 `~/.daily-work-report/config.json`，读取本地配置。
3. 从当前仓库和配置 roots 采集本地 git 证据。
4. 在已配置且可访问时采集外部证据。
5. 按身份映射过滤与用户相关的记录。
6. 为每个工作项判断状态。
7. 将工作项聚合成 2-5 条价值主线，数量按实际情况决定。
8. 使用用户模板、保存模板或默认模板渲染。
9. 只有在有帮助或用户要求时，才附短证据说明。
10. 简短说明证据缺口和不可访问来源。

## 定时日报和周报

本 Skill 可以和 Codex App 自动化、cron、launchd、systemd timer、GitHub Actions 或其他可信本地调度器配合。

推荐定时日报行为：

1. 每个工作日接近结束时运行，例如本地时间 21:50。
2. 使用当前本地日期和时区。
3. 先采集本地 git 证据。
4. 再采集已配置外部证据。
5. 生成简短日报草稿，不执行不可逆发送动作。
6. 说明不可访问来源和不确定状态。
7. 把证据和输出保存在 `.daily-report/` 这类已忽略的本地目录。

推荐定时周报行为：

1. 每周五下午运行，例如本地时间 17:50。
2. 默认统计本周一 00:00 到运行时刻。
3. 可以读取本周每日草稿做二次提炼，但必须用 git/MR 证据校验关键状态。
4. 输出“本周重点成果”和“下周重点”，不按日期流水账罗列。

定时任务默认只能生成草稿。除非用户明确配置，否则不要自动发布、发邮件、发消息或修改外部系统。

## 推荐包结构

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

## 安全边界

- 不要编造不可访问的飞书/GitLab/GitHub/Jira 内容。
- 默认不要上传源码、私有文档或内部链接到第三方服务。
- 不要暴露 secrets、token、客户内容或原始内部讨论。
- 不要把它做成员工监控工具。只使用用户授权来源和个人身份映射。
- 不要把无关 dirty files 算成交付成果。
- 不要把本地证据误写成生产上线或真实验证。

## 验证要求

输出日报/周报前检查：

- 至少检查过一个当前证据来源。
- 本地未提交工作和已合并/MR-backed 工作已分开。
- MR/PR 状态有 refs、API 或可见页面证据支撑。
- 外部来源失败已说明，没有猜测。
- 最终报告符合用户模板或明确偏好。
- 报告足够简洁，符合目标读者。

## 开源质量要求

公开发布时保持：

- 轻依赖：脚本默认只用 Python 标准库。
- 可迁移：支持 macOS/Linux 和新电脑。
- 可配置：身份、仓库 roots、来源和模板都可由用户编辑。
- 可审计：证据 JSON 可以保存和复查。
- 可扩展：connector 是通用契约，不硬编码某家公司。
