# Gmail Integration - Quick Reference

## ✅ Import Issue - FIXED!

The `ModuleNotFoundError: No module named 'integrations'` has been resolved.

## 🚀 How to Run Gmail Scripts

### Option 1: Direct Execution (Recommended)
```bash
# From project root directory
cd /Users/shibadityadeb/Desktop/ai-productivity-assistant

# Activate virtual environment
source venv/bin/activate

# Run any script
python integrations/gmail_quickstart.py
python integrations/gmail_examples.py
python integrations/gmail.py
```

### Option 2: Setup Helper Script
```bash
./setup_gmail.sh
```

### Option 3: As Python Module
```bash
python -m integrations.gmail_quickstart
python -m integrations.gmail_examples
```

## 📋 Next Steps

### 1. Get Gmail API Credentials

You need OAuth2 credentials from Google Cloud Console:

```bash
# Create credentials directory
mkdir -p credentials/
```

Then follow these steps:

1. **Go to**: https://console.cloud.google.com/
2. **Create Project**: "AI Productivity Assistant"
3. **Enable API**: Search for "Gmail API" and enable it
4. **OAuth Consent Screen**: 
   - User Type: External
   - Add your email as test user
5. **Create Credentials**:
   - Type: OAuth client ID
   - Application type: Desktop app
   - Download JSON file
6. **Save as**: `credentials/gmail_credentials.json`

**Detailed Guide**: See `integrations/GMAIL_SETUP.md`

### 2. Test Your Setup

```bash
# This will guide you through OAuth authentication
python integrations/gmail_quickstart.py
```

First run will:
1. Open your browser for OAuth consent
2. Ask you to log in with Google
3. Request permissions for Gmail access
4. Save token for future use

### 3. Run Examples

```bash
# Run all examples
python integrations/gmail_examples.py

# Run specific example (1-8)
python integrations/gmail_examples.py 2
```

## 💡 Usage in Your Code

```python
from integrations.gmail import GmailClient

# Initialize client
client = GmailClient(
    credentials_file='credentials/gmail_credentials.json',
    token_file='credentials/gmail_token.pickle'
)

# Authenticate (opens browser on first run only)
client.authenticate()

# Get important emails
important = client.get_important_emails(max_results=10)

for email in important:
    print(f"Subject: {email['subject']}")
    print(f"From: {email['from']}")
    print(f"Snippet: {email['snippet']}")
    print(f"Unread: {email['is_unread']}")
    print("-" * 80)

# Get starred emails
starred = client.get_starred_emails()

# Search with custom query
results = client.search_emails('from:boss@company.com is:unread')

# Send email
client.send_email(
    to='recipient@example.com',
    subject='Test',
    body='Hello from Python!'
)

# Mark as read
client.mark_as_read(email['id'])
```

## 🔍 Available Methods

| Method | Description |
|--------|-------------|
| `authenticate()` | OAuth2 login (one-time browser popup) |
| `get_profile()` | Get email address and stats |
| `get_important_emails()` | Fetch important emails |
| `get_starred_emails()` | Fetch starred emails |
| `get_unread_emails()` | Fetch unread emails |
| `search_emails(query)` | Custom Gmail search |
| `send_email()` | Send email with attachments |
| `mark_as_read()` | Mark as read |
| `mark_as_starred()` | Star email |

## 🐛 Troubleshooting

### "Credentials file not found"
```bash
# Make sure you're in the right directory
pwd
# Should show: /Users/.../ai-productivity-assistant

# Check if credentials exist
ls -la credentials/
```

### "Access blocked" during OAuth
- Your email must be added as a test user in OAuth consent screen
- App must be in "Testing" status (not Production)

### Import still not working
```bash
# Ensure you're running from project root
cd /Users/shibadityadeb/Desktop/ai-productivity-assistant

# Verify Python can see the module
python -c "import integrations.gmail; print('OK')"
```

## 📚 Documentation Files

- `integrations/README.md` - Quick start guide
- `integrations/GMAIL_SETUP.md` - Complete setup with screenshots
- `integrations/gmail.py` - Main implementation (650+ lines)
- `integrations/gmail_examples.py` - 8 working examples
- `integrations/gmail_quickstart.py` - Setup verification

## 🎯 Common Use Cases

### Daily Email Summary
```python
client = GmailClient()
client.authenticate()

unread = client.get_unread_emails(max_results=50)
important = client.get_important_emails(max_results=20)

print(f"📧 {len(unread)} unread emails")
print(f"⚠️  {len(important)} important emails")
```

### Monitor Specific Sender
```python
emails = client.search_emails('from:boss@company.com is:unread')
for email in emails:
    print(f"New email from boss: {email['subject']}")
    # Send Slack notification, etc.
```

### Auto-Star Urgent Emails
```python
unread = client.get_unread_emails()
for email in unread:
    if 'urgent' in email['subject'].lower():
        client.mark_as_starred(email['id'])
        print(f"⭐ Starred urgent: {email['subject']}")
```

## ✅ Status

- ✅ Import errors fixed
- ✅ All scripts executable from project root
- ✅ Ready for Gmail API credentials
- ✅ Examples and documentation complete

## 🚦 Ready to Use!

Once you have credentials:
1. Download `credentials.json` from Google Cloud
2. Save as `credentials/gmail_credentials.json`
3. Run `python integrations/gmail_quickstart.py`
4. Complete OAuth flow in browser (one time only)
5. Start using Gmail API in your app! 🎉
