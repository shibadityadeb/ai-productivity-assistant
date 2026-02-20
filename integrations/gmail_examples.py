"""
Example scripts demonstrating Gmail API integration usage.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.gmail import GmailClient
import json
from datetime import datetime


def example_1_basic_auth():
    """Example 1: Basic Authentication and Profile."""
    print("=" * 80)
    print("Example 1: Basic Authentication")
    print("=" * 80)
    
    # Initialize client
    client = GmailClient(
        credentials_file='credentials/gmail_credentials.json',
        token_file='credentials/gmail_token.pickle'
    )
    
    # Authenticate
    print("\n🔐 Authenticating with Gmail...")
    client.authenticate()
    
    # Get profile
    profile = client.get_profile()
    print(f"\n✓ Authenticated as: {profile['emailAddress']}")
    print(f"✓ Messages total: {profile.get('messagesTotal', 'N/A')}")
    print(f"✓ Threads total: {profile.get('threadsTotal', 'N/A')}")


def example_2_important_emails():
    """Example 2: Fetch and Display Important Emails."""
    print("\n" + "=" * 80)
    print("Example 2: Important Emails")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    print("\n📧 Fetching important emails...")
    important = client.get_important_emails(max_results=5)
    
    if not important:
        print("No important emails found.")
        return
    
    for i, email in enumerate(important, 1):
        print(f"\n{i}. {email['subject']}")
        print(f"   From: {email['from']}")
        print(f"   Date: {email['date']}")
        print(f"   Unread: {'✉️ ' if email['is_unread'] else '✓'}")
        print(f"   Snippet: {email['snippet'][:100]}...")


def example_3_starred_emails():
    """Example 3: Fetch Starred Emails."""
    print("\n" + "=" * 80)
    print("Example 3: Starred Emails")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    print("\n⭐ Fetching starred emails...")
    starred = client.get_starred_emails(max_results=5)
    
    if not starred:
        print("No starred emails found.")
        return
    
    for i, email in enumerate(starred, 1):
        print(f"\n{i}. ⭐ {email['subject']}")
        print(f"   From: {email['from']}")
        print(f"   Date: {email['date']}")


def example_4_search_emails():
    """Example 4: Search Emails with Custom Query."""
    print("\n" + "=" * 80)
    print("Example 4: Search Emails")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    # Example searches
    queries = [
        'is:unread',
        'from:noreply@github.com',
        'has:attachment',
        'subject:urgent'
    ]
    
    for query in queries:
        print(f"\n🔍 Searching: {query}")
        results = client.search_emails(query, max_results=3)
        print(f"   Found {len(results)} results")
        
        for email in results[:2]:
            print(f"   - {email['subject'][:60]}...")


def example_5_inbox_summary():
    """Example 5: Complete Inbox Summary."""
    print("\n" + "=" * 80)
    print("Example 5: Inbox Summary")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    print("\n📊 Generating inbox summary...\n")
    
    # Fetch various categories
    important = client.get_important_emails(max_results=10)
    starred = client.get_starred_emails(max_results=10)
    unread = client.get_unread_emails(max_results=20)
    
    # Create summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'important_count': len(important),
        'starred_count': len(starred),
        'unread_count': len(unread),
        'top_senders': _get_top_senders(important + starred + unread),
        'recent_important': [
            {
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date'],
                'is_unread': email['is_unread']
            }
            for email in important[:5]
        ]
    }
    
    # Display summary
    print(f"📥 Important emails: {summary['important_count']}")
    print(f"⭐ Starred emails: {summary['starred_count']}")
    print(f"✉️  Unread emails: {summary['unread_count']}")
    
    print("\n👥 Top Senders:")
    for sender, count in summary['top_senders'][:5]:
        print(f"   {count}x - {sender}")
    
    print("\n📧 Recent Important Emails:")
    for email in summary['recent_important']:
        status = "📩" if email['is_unread'] else "✓"
        print(f"   {status} {email['subject'][:60]}")
        print(f"      From: {email['from']}")


def example_6_mark_as_read():
    """Example 6: Process Unread Emails."""
    print("\n" + "=" * 80)
    print("Example 6: Process Unread Emails")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    print("\n📨 Fetching unread emails...")
    unread = client.get_unread_emails(max_results=5)
    
    if not unread:
        print("No unread emails found.")
        return
    
    print(f"Found {len(unread)} unread emails\n")
    
    for email in unread:
        print(f"Processing: {email['subject'][:60]}")
        print(f"From: {email['from']}")
        
        # Check if urgent
        if 'urgent' in email['subject'].lower() or 'important' in email['subject'].lower():
            print("   ⭐ Marking as starred (urgent)")
            client.mark_as_starred(email['id'])
        
        # Mark as read
        print("   ✓ Marking as read")
        client.mark_as_read(email['id'])
        print()


def example_7_send_email():
    """Example 7: Send Email."""
    print("\n" + "=" * 80)
    print("Example 7: Send Email")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    # Get profile to send to self
    profile = client.get_profile()
    email_address = profile['emailAddress']
    
    print(f"\n📤 Sending test email to {email_address}...")
    
    result = client.send_email(
        to=email_address,
        subject='Test Email from Gmail API Integration',
        body='''Hello!

This is a test email sent from the Gmail API integration.

Features demonstrated:
- OAuth2 authentication
- Email sending via API
- Plain text formatting

Timestamp: ''' + datetime.now().isoformat()
    )
    
    print(f"✓ Email sent successfully!")
    print(f"  Message ID: {result['id']}")
    print(f"  Thread ID: {result['threadId']}")


def example_8_advanced_search():
    """Example 8: Advanced Search Examples."""
    print("\n" + "=" * 80)
    print("Example 8: Advanced Search Examples")
    print("=" * 80)
    
    client = GmailClient()
    client.authenticate()
    
    # Advanced search queries
    searches = [
        {
            'name': 'Large Attachments (>5MB)',
            'query': 'has:attachment larger:5M'
        },
        {
            'name': 'Emails from last 7 days',
            'query': 'newer_than:7d'
        },
        {
            'name': 'Unread Important',
            'query': 'is:unread is:important'
        },
        {
            'name': 'GitHub Notifications',
            'query': 'from:notifications@github.com'
        }
    ]
    
    for search in searches:
        print(f"\n🔍 {search['name']}")
        print(f"   Query: {search['query']}")
        
        results = client.search_emails(search['query'], max_results=5)
        print(f"   Results: {len(results)}")
        
        for email in results[:3]:
            print(f"   - {email['subject'][:50]}...")


def _get_top_senders(emails):
    """Helper function to get top email senders."""
    from collections import Counter
    
    senders = [email['from'] for email in emails]
    # Extract email address from format like "Name <email@example.com>"
    clean_senders = []
    for sender in senders:
        if '<' in sender:
            email = sender.split('<')[1].split('>')[0]
            clean_senders.append(email)
        else:
            clean_senders.append(sender)
    
    return Counter(clean_senders).most_common(10)


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "=" * 80)
    print("Gmail API Integration - Example Demonstrations")
    print("=" * 80)
    
    try:
        example_1_basic_auth()
        example_2_important_emails()
        example_3_starred_emails()
        example_4_search_emails()
        example_5_inbox_summary()
        
        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80)
        
        # Optional: Uncomment to test these
        # example_6_mark_as_read()  # Will modify emails
        # example_7_send_email()     # Will send email
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run specific example
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        example_func = f"example_{example_num}"
        
        if example_func in globals():
            globals()[example_func]()
        else:
            print(f"Example {example_num} not found")
            print("Available examples: 1-8")
    else:
        # Run all examples
        run_all_examples()
