# GitHub 连接器规范

用途：采集配置用户相关的 Pull Request、分支状态、checks 和合并状态。

推荐 API 数据：

- PR number
- 标题
- head branch
- base branch
- 作者
- assignee / reviewer
- state
- merged timestamp
- URL
- check suite conclusion

状态映射：

- open PR -> `mr_open`
- merged PR -> `merged`
- 已推分支但没有 PR -> `pushed_branch`
- check suite 通过/失败 -> 只能作为证据说明，不等于生产证明
