# Gmail API Integration - Complete Setup Guide

## 📚 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google Cloud Console Setup](#google-cloud-console-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [API Methods Reference](#api-methods-reference)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.10+
- Google account with Gmail
- Access to Google Cloud Console

---

## Google Cloud Console Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `AI Productivity Assistant`
4. Click **"Create"**
5. Wait for project creation (may take a few seconds)

### Step 2: Enable Gmail API

1. In the Cloud Console, make sure your project is selected
2. Navigate to **APIs & Services** → **Library**
3. Search for **"Gmail API"**
4. Click on **Gmail API**
5. Click **"Enable"** button
6. Wait for API to be enabled

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **"External"** user type (unless you have Google Workspace)
3. Click **"Create"**

#### Fill in Required Information:
- **App name**: `AI Productivity Assistant`
- **User support email**: Your email address
- **Developer contact email**: Your email address
- Click **"Save and Continue"**

#### Add Scopes:
4. Click **"Add or Remove Scopes"**
5. Filter and select these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.labels`
6. Click **"Update"**
7. Click **"Save and Continue"**

#### Add Test Users:
8. Click **"Add Users"**
9. Add your Gmail address
10. Click **"Add"**
11. Click **"Save and Continue"**

### Step 4: Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Select **Application type**: `Desktop app`
4. Enter **Name**: `Gmail Desktop Client`
5. Click **"Create"**
6. A popup will show your **Client ID** and **Client Secret**
7. Click **"Download JSON"**
8. Save the file as `gmail_credentials.json`

### Step 5: Move Credentials File

```bash
# Create credentials directory
mkdir -p credentials/

# Move downloaded file to credentials directory
mv ~/Downloads/client_secret_*.json credentials/gmail_credentials.json

# Verify file exists
ls -la credentials/
```

---

## Installation

### 1. Install Required Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Install Gmail API dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

These are already in your `requirements.txt`, but if you need to add them:

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "from integrations.gmail import GmailClient; print('✓ Gmail integration ready')"
```

---

## Configuration

### Directory Structure

```
ai-productivity-assistant/
├── credentials/
│   ├── gmail_credentials.json    # OAuth2 credentials (download from Google)
│   └── gmail_token.pickle        # Auto-generated after first auth
├── integrations/
│   └── gmail.py                  # Gmail client module
└── .gitignore                    # Ensure credentials/ is ignored
```

### Verify .gitignore

Make sure your `.gitignore` includes:

```
# Credentials
credentials/
*.json
!.env.example
```

---

## Usage Examples

### Example 1: Basic Authentication & Profile

```python
from integrations.gmail import GmailClient

# Initialize client
client = GmailClient(
    credentials_file='credentials/gmail_credentials.json',
    token_file='credentials/gmail_token.pickle'
)

# Authenticate (will open browser for OAuth flow on first run)
client.authenticate()

# Get profile information
profile = client.get_profile()
print(f"Authenticated as: {profile['emailAddress']}")
```

### Example 2: Fetch Important Emails

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

# Get important emails
important_emails = client.get_important_emails(max_results=10)

for email in important_emails:
    print(f"Subject: {email['subject']}")
    print(f"From: {email['from']}")
    print(f"Date: {email['date']}")
    print(f"Snippet: {email['snippet']}")
    print(f"Unread: {email['is_unread']}")
    print("-" * 80)
```

### Example 3: Fetch Starred Emails

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

# Get starred emails
starred_emails = client.get_starred_emails(max_results=5)

for email in starred_emails:
    print(f"⭐ {email['subject']}")
    print(f"   From: {email['from']}")
    print(f"   Snippet: {email['snippet'][:100]}...")
    print()
```

### Example 4: Search Emails with Custom Query

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

# Search for specific emails
# Gmail query syntax: https://support.google.com/mail/answer/7190
emails = client.search_emails(
    query='from:notifications@github.com subject:pull request',
    max_results=10
)

print(f"Found {len(emails)} matching emails")
```

### Example 5: Send Email

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

# Send email
result = client.send_email(
    to='recipient@example.com',
    subject='Test Email from Python',
    body='This is a test email sent via Gmail API.'
)

print(f"Email sent! Message ID: {result['id']}")
```

### Example 6: Mark Emails as Read/Starred

```python
from integrations.gmail import GmailClient

client = GmailClient()
client.authenticate()

# Get unread emails
unread = client.get_unread_emails(max_results=5)

for email in unread:
    print(f"Processing: {email['subject']}")
    
    # Mark as read
    client.mark_as_read(email['id'])
    
    # Optionally star important ones
    if 'urgent' in email['subject'].lower():
        client.mark_as_starred(email['id'])
```

### Example 7: Complete Workflow

```python
from integrations.gmail import GmailClient
import json

def analyze_inbox():
    """Comprehensive inbox analysis."""
    client = GmailClient()
    client.authenticate()
    
    # Get various email categories
    important = client.get_important_emails(max_results=10)
    starred = client.get_starred_emails(max_results=10)
    unread = client.get_unread_emails(max_results=20)
    
    # Summary
    summary = {
        'profile': client.get_profile(),
        'important_count': len(important),
        'starred_count': len(starred),
        'unread_count': len(unread),
        'recent_important': [
            {
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date']
            }
            for email in important[:5]
        ]
    }
    
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == '__main__':
    analyze_inbox()
```

---

## API Methods Reference

### Authentication

#### `authenticate(force_reauth: bool = False) -> bool`
Authenticate with Gmail API using OAuth2.
- **force_reauth**: Force re-authentication even if token exists
- **Returns**: True if successful
- **Raises**: `AuthenticationError` if authentication fails

### Reading Emails

#### `get_important_emails(max_results: int = 10, include_spam_trash: bool = False) -> List[Dict]`
Fetch emails marked as important.

#### `get_starred_emails(max_results: int = 10, include_spam_trash: bool = False) -> List[Dict]`
Fetch starred emails.

#### `get_unread_emails(max_results: int = 20, query: Optional[str] = None) -> List[Dict]`
Fetch unread emails with optional query filter.

#### `search_emails(query: str, max_results: int = 20) -> List[Dict]`
Search emails using Gmail query syntax.

**Gmail Query Examples:**
- `from:user@example.com` - From specific sender
- `to:me subject:urgent` - To you with "urgent" in subject
- `has:attachment larger:5M` - Emails with attachments > 5MB
- `after:2024/01/01 before:2024/12/31` - Date range
- `is:unread is:important` - Unread important emails

### Email Data Structure

Each email returned is a dictionary with:

```python
{
    'id': 'message_id',
    'thread_id': 'thread_id',
    'subject': 'Email Subject',
    'from': 'sender@example.com',
    'to': 'recipient@example.com',
    'cc': 'cc@example.com',
    'date': 'Thu, 20 Feb 2026 10:30:00 +0000',
    'date_parsed': datetime object,
    'snippet': 'Preview text...',
    'body': 'Full email body',
    'labels': ['INBOX', 'IMPORTANT', 'UNREAD'],
    'is_unread': True,
    'is_starred': False,
    'is_important': True
}
```

### Sending Emails

#### `send_email(to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None, attachments: Optional[List[str]] = None) -> Dict`
Send email via Gmail API with optional attachments.

### Modifying Emails

#### `mark_as_read(message_id: str) -> bool`
Mark email as read.

#### `mark_as_starred(message_id: str) -> bool`
Star an email.

### Profile

#### `get_profile() -> Dict`
Get Gmail profile information including email address.

---

## Error Handling

The client includes comprehensive error handling:

### Exception Types

```python
from integrations.gmail import (
    GmailAPIError,           # Base exception
    AuthenticationError,     # Auth failures
    RateLimitError          # Rate limit exceeded
)
```

### Handling Errors

```python
from integrations.gmail import GmailClient, GmailAPIError, AuthenticationError

client = GmailClient()

try:
    client.authenticate()
    emails = client.get_important_emails()
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Re-authenticate or check credentials
    
except RateLimitError as e:
    print(f"Rate limit hit: {e}")
    # Wait before retrying
    
except GmailAPIError as e:
    print(f"API error: {e}")
    # Handle other API errors
```

---

## Troubleshooting

### Issue 1: "Credentials file not found"

**Error**: `AuthenticationError: Credentials file not found: credentials/gmail_credentials.json`

**Solution**:
1. Verify you downloaded OAuth2 credentials from Google Cloud Console
2. Ensure file is named `gmail_credentials.json`
3. Place file in `credentials/` directory
4. Check file path: `ls -la credentials/gmail_credentials.json`

### Issue 2: "Access blocked: This app's request is invalid"

**Error**: OAuth screen shows "Access blocked" message

**Solution**:
1. Go to OAuth consent screen in Google Cloud Console
2. Add your Gmail address as a test user
3. Ensure app is in "Testing" mode (not "Production")
4. Verify all required scopes are added

### Issue 3: Token refresh fails

**Error**: `AuthenticationError: Token refresh failed`

**Solution**:
1. Delete existing token: `rm credentials/gmail_token.pickle`
2. Re-authenticate: Will trigger OAuth flow again
3. If problem persists, regenerate OAuth credentials

### Issue 4: "Invalid grant" error

**Solution**:
1. Token expired or revoked
2. Delete token file and re-authenticate
3. Check system clock is correct

### Issue 5: Rate limit errors

**Error**: `RateLimitError: Rate limit exceeded`

**Solution**:
- Client includes automatic retry with exponential backoff
- Reduce `max_results` in queries
- Add delays between bulk operations
- Check [Gmail API quotas](https://developers.google.com/gmail/api/reference/quota)

### Issue 6: Import errors

**Error**: `ModuleNotFoundError: No module named 'google'`

**Solution**:
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

---

## Security Best Practices

1. **Never commit credentials**: Ensure `credentials/` is in `.gitignore`
2. **Token security**: Treat `gmail_token.pickle` as sensitive
3. **Minimal scopes**: Only request necessary Gmail scopes
4. **Regular rotation**: Periodically regenerate OAuth credentials
5. **Test users**: Keep app in Testing mode unless publishing

---

## Gmail API Quotas & Limits

- **Per-user rate limit**: 250 quota units per second
- **Daily limit**: 1 billion quota units per day
- Most operations cost 5-10 quota units
- [Full quota documentation](https://developers.google.com/gmail/api/reference/quota)

---

## Advanced Configuration

### Custom Scopes

Modify scopes in `integrations/gmail.py`:

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read-only
    'https://www.googleapis.com/auth/gmail.send',      # Send
    'https://www.googleapis.com/auth/gmail.modify',    # Modify labels
]
```

### Custom Rate Limiting

```python
client = GmailClient()
client.min_request_interval = 0.2  # 200ms between requests
client.max_retries = 5              # More retries
```

---

## Testing

Create a test script:

```python
# test_gmail.py
from integrations.gmail import GmailClient

def test_authentication():
    client = GmailClient()
    assert client.authenticate() == True
    print("✓ Authentication successful")

def test_profile():
    client = GmailClient()
    client.authenticate()
    profile = client.get_profile()
    assert 'emailAddress' in profile
    print(f"✓ Profile retrieved: {profile['emailAddress']}")

def test_fetch_emails():
    client = GmailClient()
    client.authenticate()
    emails = client.get_important_emails(max_results=5)
    print(f"✓ Fetched {len(emails)} important emails")

if __name__ == '__main__':
    test_authentication()
    test_profile()
    test_fetch_emails()
    print("\n✓ All tests passed!")
```

Run tests:
```bash
python test_gmail.py
```

---

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)

---

## Support

For issues specific to this integration:
1. Check troubleshooting section above
2. Verify credentials setup
3. Check Gmail API quotas
4. Review Google Cloud Console logs

For Gmail API issues:
- [Stack Overflow - gmail-api tag](https://stackoverflow.com/questions/tagged/gmail-api)
- [Google API Support](https://support.google.com/googleapi)
