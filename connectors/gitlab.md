# GitLab 连接器规范

用途：采集配置身份相关的 Merge Request、分支状态、审批、pipeline 状态和合并状态。

推荐 API 数据：

- MR id / iid
- 标题
- source branch
- target branch
- 作者
- assignee
- 创建 / 更新 / 合并时间
- state
- web URL
- head SHA
- pipeline 状态

状态映射：

- open MR -> `mr_open`
- merged MR -> `merged`
- 已推分支但没有 MR -> `pushed_branch`
- pipeline 通过/失败 -> 只能作为证据说明，不等于部署证明

不要把 pipeline 通过当成生产部署或用户流程验证。
