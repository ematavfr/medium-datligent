import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv("../.env")

IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = os.environ.get("GMAIL_USER")
EMAIL_PASS = os.environ.get("GMAIL_PASS")

def check_recent():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select('"[Gmail]/Tous les messages"')
    
    # Search for "AI Logging Agents" in TEXT since Jan 17
    status, messages = mail.search(None, '(TEXT "AI Logging Agents" SINCE "17-Jan-2026")')
    if status != "OK" or not messages[0]:
        print("No emails with 'AI Logging Agents' in text found since Jan 17.")
        return

    ids = messages[0].split()
    print(f"Found {len(ids)} emails. Printing details...")
    
    for eid in reversed(ids):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                # Decoding subject
                subject = ""
                decoded = decode_header(msg["subject"] or "")
                for part, encoding in decoded:
                    if isinstance(part, bytes):
                        subject += part.decode(encoding or "utf-8", errors="ignore")
                    else:
                        subject += part
                
                print(f"Date: {msg['date']} | From: {msg['from']} | Subject: {subject}")

if __name__ == "__main__":
    check_recent()
