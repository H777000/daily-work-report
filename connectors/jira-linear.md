# Jira / Linear 连接器规范

用途：采集配置身份相关的 issue / task 流转记录。

推荐字段：

- issue id
- 标题
- assignee
- status
- 更新时间
- project
- URL
- 可用时关联 branch / MR / PR

规则：

- 任务状态只能作为计划/协作证据。
- Jira/Linear 的 `Done` 不等于代码已合并或已部署，除非有工程证据确认。
- 任务记录主要用于改进工作主线聚合和明日/下周跟进项。
