# 开源发布检查清单

发布本 Skill 前检查：

1. 移除私有 URL、姓名、证据文件和公司特定输出。
2. 明确选择开源许可证。
3. 运行 Python 语法检查：

   ```bash
   python3 -m py_compile scripts/collect_git.py scripts/render_report.py
   ```

4. 在一次性测试仓库上跑 git-only smoke test。
5. 验证这些场景：
   - 只有本地提交，没有 MR。
   - 已推分支，但没有 MR。
   - MR 已创建，但未合并。
   - MR 已合并，但本地还有 dirty worktree。
   - 外部来源不可访问。
   - 用户自定义模板。
   - 多作者仓库，只统计本人工作。
6. 确认默认报告不会把别人 fetch 下来的远端分支当成用户自己的工作。
7. 确认证据 JSON 可审计，但不保存源码或密钥。
8. 如果脚本参数变化，同步更新 README 示例。
9. 如果增加定时执行，确认默认行为只生成本地草稿，不自动发送或发布。

