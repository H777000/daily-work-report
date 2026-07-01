# daily-work-report

`daily-work-report` 是一个 Codex Skill，用真实证据生成可信的日报和周报。它可以读取本地 git 活动、MR/PR 线索、可选工作平台记录、身份映射和用户自定义模板，把技术动作整理成适合汇报的中文总结。

它的定位是 **个人工作复盘助手**，不是员工监控工具。

## 能做什么

- 扫描本地 git 仓库，识别当天/本周提交、分支、MR/PR refs、合并状态和未提交改动。
- 区分本地进度、已推分支、已提 MR/PR、已合并、已部署、已验证。
- 支持用户提供自己的日报模板和表达风格。
- 把技术证据翻译成领导能读懂的业务价值。
- 可选保存证据账本，方便用户追溯“为什么这么写”。

## 快速开始

在任意工作区运行：

```bash
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py --roots . --output .daily-report/evidence/today-git.json
python3 ~/.codex/skills/daily-work-report/scripts/render_report.py .daily-report/evidence/today-git.json
```

指定日期：

```bash
python3 ~/.codex/skills/daily-work-report/scripts/collect_git.py --roots . --date 2026-07-01 --output .daily-report/evidence/2026-07-01-git.json
python3 ~/.codex/skills/daily-work-report/scripts/render_report.py .daily-report/evidence/2026-07-01-git.json --date 2026-07-01
```

## 定时使用

可以把本 Skill 接入本地调度器，在每天工作结束前自动生成草稿。

推荐行为：

- 每天本地时间 21:50 左右生成日报草稿。
- 每周五本地时间 17:50 左右生成周总结草稿。
- 扫描配置的本地仓库。
- 补充配置的外部来源。
- 把证据写入 `.daily-report/evidence/`。
- 把输出写入 `.daily-report/outputs/`。
- 默认不自动发送、不自动发布，除非用户明确配置。

日报示例 shell 流程：

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

## 配置

复制 `config.example.json` 到以下任一位置：

```text
.daily-report/config.json
~/.daily-work-report/config.json
```

可以配置：

- 你在不同系统里的身份。
- 需要扫描的仓库路径。
- 外部证据来源链接。
- 默认报告风格。
- 产品命名前缀规则。
- 定时草稿偏好。

## 状态规则

本 Skill 不能过度承诺。它区分：

- `local_dirty`：本地未提交改动。
- `local_commit`：本地已提交。
- `pushed_branch`：已推分支。
- `mr_open`：有 MR/PR 证据。
- `merged`：分支/MR 已进入目标分支。
- `deployed`：有部署证据。
- `verified`：有运行时或真实用户流程验证证据。
- `unknown`：证据不足。

如果证据只证明“已推分支”，就不能写成“已上线”。

## 模板理念

模板不是简单替换文字，而是表达偏好。模板可以定义：

- 标题格式。
- 大标题样式。
- 大标题数量是否灵活。
- 小点是编号还是自然段。
- 是否展示 MR 细节。
- 明日计划/下周计划写法。
- 领导汇报、个人复盘、站会同步或交付说明语气。

## 隐私

默认本地优先：

- 不上传源码。
- 不主动调用外部 API，除非用户配置。
- 不猜测不可访问的私有页面。
- 不做团队监控叙事。

## 开源路线图

- 实现 GitLab/GitHub API connector。
- 实现飞书/Lark 表格读取 connector。
- 实现 Jira/Linear assignee 活动 connector。
- 增加更多评测用例。
- 增强模板理解能力。
- 补充 cron、launchd、systemd timer 和 Codex App 自动化示例。
