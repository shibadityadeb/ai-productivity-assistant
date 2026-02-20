# Gmail API Integration

Complete, production-ready Gmail API integration with OAuth2 authentication.

## 🚀 Quick Start

### 1. Setup Google Cloud Console

Follow the detailed guide: [GMAIL_SETUP.md](GMAIL_SETUP.md)

**Quick Steps:**
1. Enable Gmail API in Google Cloud Console
2. Create OAuth2 credentials (Desktop app)
3. Download credentials as `credentials/gmail_credentials.json`

### 2. Test Your Setup

```bash
# Option 1: Use setup helper script
./setup_gmail.sh

# Option 2: Run quickstart directly
python integrations/gmail_quickstart.py

# Option 3: Run as module
python -m integrations.gmail_quickstart
```

This will:
- ✓ Verify credentials file exists
- ✓ Test OAuth2 authentication
- ✓ Fetch sample emails
- ✓ Display inbox summary

### 3. Basic Usage

```python
from integrations.gmail import GmailClient

# Initialize and authenticate
client = GmailClient()
client.authenticate()  # Opens browser for OAuth on first run

# Fetch important emails
important = client.get_important_emails(max_results=10)

for email in important:
    print(f"Subject: {email['subject']}")
    print(f"From: {email['from']}")
    print(f"Snippet: {email['snippet']}")
```

## 📚 Features

### ✅ Authentication
- OAuth2 with automatic token refresh
- Secure credential storage
- Error handling and retry logic

### ✅ Read Emails
- Important emails
- Starred emails
- Unread emails
- Custom search queries
- Full Gmail query syntax support

### ✅ Send Emails
- Plain text and HTML
- Attachments support
- CC and BCC

### ✅ Modify Emails
- Mark as read/unread
- Star/unstar
- Add/remove labels

### ✅ Production Ready
- Rate limiting protection
- Exponential backoff retry
- Comprehensive error handling
- Structured logging
- Type hints throughout

## 📖 Documentation

| File | Description |
|------|-------------|
| [gmail.py](gmail.py) | Main Gmail client implementation |
| [GMAIL_SETUP.md](GMAIL_SETUP.md) | Complete setup guide with screenshots |
| [gmail_examples.py](gmail_examples.py) | 8 example scripts demonstrating all features |
| [gmail_quickstart.py](gmail_quickstart.py) | Quick verification script |

## 🔧 API Methods

### Authentication
```python
client.authenticate(force_reauth=False)
client.get_profile()
```

### Reading Emails
```python
client.get_important_emails(max_results=10)
client.get_starred_emails(max_results=10)
client.get_unread_emails(max_results=20)
client.search_emails(query='from:user@example.com', max_results=20)
```

### Sending Emails
```python
client.send_email(
    to='recipient@example.com',
    subject='Subject',
    body='Email body',
    attachments=['file.pdf']  # optional
)
```

### Modifying Emails
```python
client.mark_as_read(message_id)
client.mark_as_starred(message_id)
```

## 💡 Examples

### Fetch and Process Important Emails

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

# Get important unread emails
important = client.get_important_emails(max_results=10)

for email in important:
    if email['is_unread']:
        print(f"📩 {email['subject']}")
        print(f"   From: {email['from']}")
        
        # Auto-star urgent emails
        if 'urgent' in email['subject'].lower():
            client.mark_as_starred(email['id'])
```

### Search with Gmail Query Syntax

```python
# Find specific emails
emails = client.search_emails(
    query='from:boss@company.com subject:meeting is:unread',
    max_results=5
)

# Emails with large attachments
large_files = client.search_emails('has:attachment larger:10M')

# Recent important emails
recent = client.search_emails('is:important newer_than:7d')
```

### Inbox Summary Report

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

profile = client.get_profile()
important = client.get_important_emails(max_results=10)
unread = client.get_unread_emails(max_results=20)

print(f"📬 {profile['emailAddress']}")
print(f"📧 {len(important)} important emails")
print(f"✉️  {len(unread)} unread emails")
```

## 🎯 Use Cases

1. **Email Automation**: Auto-respond, filter, or forward emails
2. **Inbox Analytics**: Analyze email patterns and productivity
3. **Alert System**: Monitor for specific emails and trigger actions
4. **Backup**: Archive important emails programmatically
5. **Integration**: Connect Gmail with other services (Slack, Toggl, etc.)

## 🔐 Security

- ✅ OAuth2 authentication (no password storage)
- ✅ Tokens stored locally with pickle
- ✅ Automatic token refresh
- ✅ Credentials in `.gitignore`
- ✅ Minimal required scopes

## 🐛 Troubleshooting

### "Credentials file not found"
```bash
# Ensure file exists
ls -la credentials/gmail_credentials.json

# If missing, download from Google Cloud Console
```

### "Access blocked" during OAuth
- Add your email as test user in OAuth consent screen
- Ensure app is in "Testing" mode

### Import errors
```bash
# Install missing packages
pip install google-auth google-auth-oauthlib google-api-python-client

# If you see "ModuleNotFoundError: No module named 'integrations'"
# Run from project root directory
cd /path/to/ai-productivity-assistant
python integrations/gmail_quickstart.py
```

### Module not found error
If you get `ModuleNotFoundError: No module named 'integrations'`:
- Make sure you're running from the project root directory
- Scripts are already configured to fix this automatically
- Alternatively, use: `python -m integrations.gmail_quickstart`

**Full troubleshooting guide**: [GMAIL_SETUP.md](GMAIL_SETUP.md#troubleshooting)

## 📊 Rate Limits

- Per-user: 250 quota units/second
- Daily: 1 billion quota units/day
- Client includes automatic rate limiting and retry

## 🧪 Testing

Run all example scripts:
```bash
# All examples
python integrations/gmail_examples.py

# Specific example (1-8)
python integrations/gmail_examples.py 2
```

Run quick verification:
```bash
python integrations/gmail_quickstart.py
```

## 📦 Dependencies

```
google-auth>=2.36.0
google-auth-oauthlib>=1.2.1
google-auth-httplib2>=0.2.0
google-api-python-client>=2.154.0
structlog>=24.4.0
```

All included in main `requirements.txt`.

## 🔗 Resources

- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

---

**Created for**: AI Productivity Assistant  
**Author**: Production-Ready Gmail Integration  
**License**: MIT
