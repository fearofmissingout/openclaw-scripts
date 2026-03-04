# 阿里邮箱监控 (Aliyun Mail Monitor)

用于监控阿里企业邮箱的未读邮件，并推送到 Telegram。

## 功能

1. **未读邮件检查** - 每小时自动检查未读邮件，有新邮件时推送到 Telegram
2. **每日邮件摘要** - 每天 18:00 自动生成邮件摘要报告
3. **标记已读** - 支持手动标记邮件为已读

## 文件说明

| 文件 | 功能 |
|------|------|
| `notify-simple.py` | 未读邮件检查和通知脚本 |
| `aliyun-mail-telegram.py` | 邮件摘要生成脚本 |
| `mark-simple.py` | 标记所有邮件为已读 |
| `.env` | 配置文件（**不包含在仓库中**）|

## 环境变量

需要配置以下环境变量（或在 `.env` 文件中）：

```bash
ALIYUN_EMAIL=your@email.com
ALIYUN_EMAIL_PASSWORD=your-app-password
```

### 获取阿里邮箱应用密码

1. 登录阿里邮箱管理后台
2. 设置 → 账号安全 → 开启 IMAP/SMTP
3. 设置独立密码或应用密码

## 使用方法

### 检查未读邮件

```bash
python notify-simple.py --notify --chat-id "YOUR_CHAT_ID" --bot-token "YOUR_BOT_TOKEN"
```

参数说明：
- `--notify` - 发送通知
- `--chat-id` - Telegram 聊天 ID（群或用户）
- `--bot-token` - Telegram Bot Token
- `--max-display` - 最大显示数量（默认 10）

### 每日摘要

```bash
python aliyun-mail-telegram.py --recent 20 --chat-id "YOUR_CHAT_ID" --bot-token "YOUR_BOT_TOKEN"
```

### 标记全部已读

```bash
python mark-simple.py
```

## OpenClaw 定时任务配置

### 每小时检查未读

```bash
openclaw cron add
```

配置：
- schedule: every 1 hour
- command: 运行 notify-simple.py

### 每天 18:00 邮件摘要

```bash
openclaw cron add
```

配置：
- schedule: cron `0 18 * * *` (北京时间)
- command: 运行 aliyun-mail-telegram.py

## Telegram 群配置

需要在 OpenClaw 配置中允许群聊：

```json
{
  "channels": {
    "telegram": {
      "groups": {
        "YOUR_GROUP_ID": {
          "requireMention": true,
          "groupPolicy": "open"
        }
      }
    }
  }
}
```

## 安全注意

- **不要提交 `.env` 文件到仓库！**
- 使用环境变量或 CI/CD 密钥管理
- 定期更换应用密码
