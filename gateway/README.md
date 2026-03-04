# Gateway 监控脚本

用于监控 OpenClaw Gateway 状态，Gateway 挂掉时自动重启。

## 功能

- 每 30 秒检查一次 Gateway 健康状态
- 检测到 Gateway 不可用时自动重启
- 记录日志到文件

## 环境变量

无

## 使用方法

```powershell
powershell -ExecutionPolicy Bypass -File gateway-watch.ps1
```

## 日志

日志文件位置：`$env:USERPROFILE\.openclaw\logs\gateway-watch.log`

## Windows 开机自启

将脚本添加到 Windows 开机启动：

1. 按 `Win + R`，输入 `shell:startup`
2. 创建快捷方式指向脚本

或使用任务计划程序：

```powershell
schtasks /create /tn "OpenClaw Gateway Watch" /tr "powershell -ExecutionPolicy Bypass -File C:\path\to\gateway-watch.ps1" /sc onstart
```
