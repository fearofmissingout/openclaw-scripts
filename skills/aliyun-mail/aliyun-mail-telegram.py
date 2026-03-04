#!/usr/bin/env python3
"""
Aliyun Enterprise Mail Checker with Telegram Notification
Usage: python aliyun-mail-telegram.py [--unread] [--chat-id ID] [--bot-token TOKEN]
"""

import os
import sys
import argparse
import imbox
import socket
import urllib.request
import urllib.parse
import json
from pathlib import Path

# Load .env file if exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Default Aliyun IMAP settings
DEFAULT_IMAP_HOST = "imap.mxhichina.com"
DEFAULT_IMAP_PORT = 993
socket.setdefaulttimeout(30)

def send_telegram_message(bot_token, chat_id, text):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                print(f"Message sent to {chat_id}")
                return True
            else:
                print(f"Error: {result.get('description')}")
                return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def get_emails(host=None, port=None, username=None, password=None, unread_only=True, max_emails=5):
    """Fetch emails from Aliyun enterprise mail"""
    
    host = host or os.environ.get('ALIYUN_IMAP_HOST', DEFAULT_IMAP_HOST)
    port = port or int(os.environ.get('ALIYUN_IMAP_PORT', DEFAULT_IMAP_PORT))
    username = username or os.environ.get('ALIYUN_EMAIL')
    password = password or os.environ.get('ALIYUN_EMAIL_PASSWORD')
    
    if not username or not password:
        print("Error: Missing email credentials")
        print("Set ALIYUN_EMAIL and ALIYUN_EMAIL_PASSWORD in .env file or environment")
        sys.exit(1)
    
    try:
        mailbox = imbox.Imbox(host, username, password, port=port, ssl=True)
        print(f"Connected to {host}")
            
        if unread_only:
            all_messages = mailbox.messages(unread=True)
        else:
            all_messages = mailbox.messages()
        
        email_list = []
        for uid, message in all_messages:
            try:
                from_email = message.sent_from[0]['email'] if message.sent_from else 'Unknown'
                from_name = message.sent_from[0]['name'] if message.sent_from else 'Unknown'
            except:
                from_email = 'Unknown'
                from_name = 'Unknown'
            
            subject = message.subject or '(No Subject)'
            
            email_list.append({
                'uid': uid,
                'from': from_email,
                'name': from_name,
                'subject': subject,
                'date': str(message.date),
            })
            
            if len(email_list) >= max_emails:
                break
        
        mailbox.logout()
        return email_list
    
    except Exception as e:
        print(f"Error connecting to mail server: {e}")
        sys.exit(1)

def main():
    # Fix Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(description='Check Aliyun email and notify via Telegram')
    parser.add_argument('--unread', action='store_true', help='Show only unread emails')
    parser.add_argument('--recent', type=int, default=5, help='Number of recent emails to show')
    parser.add_argument('--chat-id', type=str, help='Telegram chat ID (group or user)')
    parser.add_argument('--bot-token', type=str, help='Telegram bot token')
    parser.add_argument('--host', type=str, help='IMAP host')
    parser.add_argument('--port', type=int, help='IMAP port')
    parser.add_argument('--username', type=str, help='Email username')
    parser.add_argument('--password', type=str, help='Email password')
    
    args = parser.parse_args()
    
    emails = get_emails(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        unread_only=args.unread,
        max_emails=args.recent
    )
    
    # Format message
    if args.unread:
        message = f"📬 <b>你有 {len(emails)} 封未读邮件:</b>\n\n"
    else:
        message = f"📧 <b>最近 {len(emails)} 封邮件:</b>\n\n"
    
    for i, email in enumerate(emails, 1):
        # Truncate long subjects
        subject = email['subject'][:50] + '...' if len(email['subject']) > 50 else email['subject']
        message += f"{i}. <b>{email['name']}</b>\n"
        message += f"   📝 {subject}\n\n"
    
    # Add footer
    message += f"---\n🤖 阿里邮箱监控"
    
    print(message)
    
    # Send to Telegram if chat_id and token provided
    if args.chat_id and args.bot_token:
        print(f"\n正在发送到 Telegram...")
        send_telegram_message(args.bot_token, args.chat_id, message)
    elif args.chat_id or args.bot_token:
        print("\nError: 需要同时提供 --chat-id 和 --bot-token 才能发送到 Telegram")

if __name__ == "__main__":
    main()
