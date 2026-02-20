#!/usr/bin/env python3
"""
Gmail API Quick Start - Verify your setup and test authentication
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.gmail import GmailClient, AuthenticationError


def check_credentials():
    """Check if credentials file exists."""
    creds_file = Path('credentials/gmail_credentials.json')
    
    if not creds_file.exists():
        print("❌ Credentials file not found!")
        print("\n📋 Setup Instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Gmail API")
        print("3. Create OAuth2 credentials (Desktop app)")
        print("4. Download credentials.json")
        print("5. Save as: credentials/gmail_credentials.json")
        print("\n📖 Detailed guide: integrations/GMAIL_SETUP.md")
        return False
    
    print("✓ Credentials file found")
    return True


def test_authentication():
    """Test Gmail API authentication."""
    print("\n🔐 Testing authentication...")
    
    try:
        client = GmailClient(
            credentials_file='credentials/gmail_credentials.json',
            token_file='credentials/gmail_token.pickle'
        )
        
        # Authenticate
        client.authenticate()
        print("✓ Authentication successful")
        
        # Get profile
        profile = client.get_profile()
        print(f"✓ Connected to: {profile['emailAddress']}")
        print(f"✓ Total messages: {profile.get('messagesTotal', 'N/A')}")
        
        return True
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_basic_operations():
    """Test basic Gmail operations."""
    print("\n📧 Testing basic operations...")
    
    try:
        client = GmailClient()
        client.authenticate()
        
        # Test fetching emails
        print("  - Fetching important emails...", end=" ")
        important = client.get_important_emails(max_results=3)
        print(f"✓ Found {len(important)}")
        
        print("  - Fetching starred emails...", end=" ")
        starred = client.get_starred_emails(max_results=3)
        print(f"✓ Found {len(starred)}")
        
        print("  - Fetching unread emails...", end=" ")
        unread = client.get_unread_emails(max_results=3)
        print(f"✓ Found {len(unread)}")
        
        print("  - Testing search...", end=" ")
        results = client.search_emails('is:inbox', max_results=3)
        print(f"✓ Found {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def display_sample_emails():
    """Display sample emails."""
    print("\n📬 Sample Important Emails:")
    print("-" * 80)
    
    try:
        client = GmailClient()
        client.authenticate()
        
        important = client.get_important_emails(max_results=3)
        
        if not important:
            print("No important emails found.")
            return
        
        for i, email in enumerate(important, 1):
            print(f"\n{i}. {email['subject']}")
            print(f"   From: {email['from']}")
            print(f"   Date: {email['date']}")
            print(f"   Unread: {'Yes ✉️' if email['is_unread'] else 'No ✓'}")
            print(f"   Preview: {email['snippet'][:80]}...")
        
    except Exception as e:
        print(f"Error fetching emails: {e}")


def main():
    """Run quick start tests."""
    print("=" * 80)
    print("Gmail API Integration - Quick Start Test")
    print("=" * 80)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    # Check Python packages
    try:
        import google.auth
        import google_auth_oauthlib
        import googleapiclient
        print("✓ Required packages installed")
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
        sys.exit(1)
    
    # Check credentials
    if not check_credentials():
        sys.exit(1)
    
    # Test authentication
    if not test_authentication():
        sys.exit(1)
    
    # Test operations
    if not test_basic_operations():
        sys.exit(1)
    
    # Display samples
    display_sample_emails()
    
    # Success
    print("\n" + "=" * 80)
    print("✅ All tests passed! Gmail integration is ready to use.")
    print("=" * 80)
    print("\n📚 Next Steps:")
    print("  - Review examples: python integrations/gmail_examples.py")
    print("  - Read setup guide: integrations/GMAIL_SETUP.md")
    print("  - Integrate with your app: from integrations.gmail import GmailClient")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
