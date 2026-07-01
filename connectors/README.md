# 连接器契约

连接器负责把外部工作平台记录转换成和本地 git 采集一致的证据结构。

连接器输出的 JSON 记录至少应包含：

```json
{
  "source": "feishu",
  "type": "task_row",
  "title": "简短标题",
  "date": "2026-07-01",
  "author_or_owner": "用户姓名",
  "author_match": true,
  "status": "unknown",
  "url": "https://...",
  "summary": "人类可读摘要",
  "confidence": "medium",
  "raw_ref": "表格行 id 或外部系统 id"
}
```

规则：

- 默认不要保存密钥或原始私密内容。
- 明确标记不可访问来源。
- 纳入用户报告前必须先做身份映射。
- 外部证据用于补充本地证据，不能替代本地证据。
