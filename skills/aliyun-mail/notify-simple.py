#!/usr/bin/env python3
"""
Aliyun Enterprise Mail - Check unread and notify ONLY if there are unread emails
"""

import os
import sys
import imbox
import socket
import urllib.request
import urllib.parse
import json
import re
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

DEFAULT_IMAP_HOST = "imap.mxhichina.com"
DEFAULT_IMAP_PORT = 993
socket.setdefaulttimeout(30)

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = re.sub(r'http[s]?://\S+', '', text)
    text = ' '.join(text.split())
    return text

def get_unread_count():
    """Get count of unread emails"""
    host = os.environ.get('ALIYUN_IMAP_HOST', DEFAULT_IMAP_HOST)
    port = int(os.environ.get('ALIYUN_IMAP_PORT', DEFAULT_IMAP_PORT))
    username = os.environ.get('ALIYUN_EMAIL')
    password = os.environ.get('ALIYUN_EMAIL_PASSWORD')
    
    mailbox = imbox.Imbox(host, username, password, port=port, ssl=True)
    
    messages = mailbox.messages(unread=True)
    count = 0
    for uid, msg in messages:
        count += 1
    
    mailbox.logout()
    return count

def get_unread_emails(max_emails=10):
    """Get list of unread emails (limited)"""
    host = os.environ.get('ALIYUN_IMAP_HOST', DEFAULT_IMAP_HOST)
    port = int(os.environ.get('ALIYUN_IMAP_PORT', DEFAULT_IMAP_PORT))
    username = os.environ.get('ALIYUN_EMAIL')
    password = os.environ.get('ALIYUN_EMAIL_PASSWORD')
    
    mailbox = imbox.Imbox(host, username, password, port=port, ssl=True)
    
    messages = mailbox.messages(unread=True)
    
    emails = []
    for uid, msg in messages:
        if len(emails) >= max_emails:
            break
        
        body = ''
        if msg.body:
            if isinstance(msg.body, dict):
                for key in ['plain', 'text', '']:
                    if key in msg.body:
                        body = str(msg.body[key])
                        break
            else:
                body = str(msg.body)
        
        body = clean_text(body)[:100]
        
        emails.append({
            'uid': str(uid),
            'from_email': msg.sent_from[0]['email'] if msg.sent_from else '',
            'from_name': msg.sent_from[0]['name'] if msg.sent_from else 'Unknown',
            'subject': clean_text(msg.subject or '(无主题)'),
            'body': body
        })
    
    mailbox.logout()
    return emails

def send_notification(bot_token, chat_id, emails):
    """Send notification with subject, sender, and preview"""
    
    text = f"📬 <b>你有 {len(emails)} 封未读邮件：</b>\n\n"
    
    for i, email in enumerate(emails):
        text += f"━━━━━━━━━━━━━━━━━━━━\n"
        text += f"<b>{i+1}. {email['from_name']}</b>\n"
        text += f"📝 {email['subject']}\n"
        if email['body']:
            text += f"📄 摘要: {email['body'][:80]}...\n"
        text += "\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "回复 <b>读1</b> 或 <b>第1封</b> 查看详情"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8')).get('ok', False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--notify', action='store_true')
    parser.add_argument('--chat-id')
    parser.add_argument('--bot-token')
    parser.add_argument('--max-display', type=int, default=10)
    
    args = parser.parse_args()
    
    if args.notify and args.chat_id and args.bot_token:
        # First get total unread count
        total_unread = get_unread_count()
        
        if total_unread == 0:
            print(f"No unread emails, skipping notification")
        else:
            # Get emails to display
            emails = get_unread_emails(max_emails=args.max_display)
            ok = send_notification(args.bot_token, args.chat_id, emails)
            if ok:
                print(f"Sent notification: {len(emails)} emails shown (total: {total_unread})")
            else:
                print("Failed to send notification")
