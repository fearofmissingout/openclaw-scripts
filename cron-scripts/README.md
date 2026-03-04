# 定时任务脚本

## 阿里邮箱监控

详见 `../skills/aliyun-mail/README.md`

## 使用 OpenClaw Cron

查看当前定时任务：

```bash
openclaw cron list
```

添加新任务：

```bash
openclaw cron add
```

任务配置示例：

```json
{
  "name": "check-email-unread",
  "schedule": {
    "kind": "every",
    "everyMs": 3600000  // 1小时
  },
  "payload": {
    "kind": "agentTurn",
    "message": "运行 Python 脚本检查未读邮件..."
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "telegram:YOUR_CHAT_ID"
  }
}
```
