# OpenClaw Scripts

OpenClaw 自动化脚本集合，包含邮件监控、定时任务、技能脚本等。

## 目录结构

```
openclaw-scripts/
├── skills/              # OpenClaw Skills 脚本
│   ├── aliyun-mail/   # 阿里邮箱监控
│   └── ...
├── cron-scripts/       # 定时任务脚本
├── utilities/          # 工具脚本
├── gateway/           # Gateway 监控脚本
└── README.md
```

## 功能列表

### 阿里邮箱监控 (skills/aliyun-mail)
- 未读邮件检查和通知
- 定时邮件摘要
- 标记已读功能

详见 [aliyun-mail/README.md](skills/aliyun-mail/README.md)

## 环境变量

部分脚本需要以下环境变量：
- `ALIYUN_EMAIL` - 阿里邮箱账号
- `ALIYUN_EMAIL_PASSWORD` - 阿里邮箱应用密码
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token

**注意：不要提交包含真实凭证的配置文件！**

## 使用方法

具体使用说明请参考各目录下的 README.md
