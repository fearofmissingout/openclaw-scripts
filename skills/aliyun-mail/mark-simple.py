import imaplib

print("Connecting...")
conn = imaplib.IMAP4_SSL('imap.mxhichina.com')
print("Logging in...")
conn.login('zuiyang.shen@lianwei.com.cn', 'vO9NBicxYWbnFl0E')
print("Selecting inbox...")
conn.select('INBOX')
print("Searching unread...")
typ, data = conn.search(None, 'UNSEEN')
unread_ids = [s.decode() for s in data[0].split() if s]
print(f"Found {len(unread_ids)} unread")
if unread_ids:
    # Mark as read in batches of 100
    for i in range(0, len(unread_ids), 100):
        batch = unread_ids[i:i+100]
        conn.store(','.join(batch), '+FLAGS', '\\Seen')
    print(f"Marked {len(unread_ids)} as read")
conn.logout()
print("Done!")
