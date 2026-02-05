#!/usr/bin/env python3
"""
Black Crab Park Blog Bot - Main Controller

This bot automates posting to the Black Crab Park blog on Blogger.
It can:
- Generate content using local Ollama AI or templates
- Post to Blogger on a 3-day schedule
- Run as a daemon or cron job
- Queue posts for later publishing

Usage:
    python bot.py                    # Interactive menu
    python bot.py --status           # Show status
    python bot.py --post             # Post now
    python bot.py --schedule         # Start scheduler
    python bot.py --setup            # Setup wizard
"""

import sys
import os
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import BLOG_CONFIG, AI_CONFIG, PATHS
from blogger_api import get_client, GOOGLE_API_AVAILABLE
from content_generator import ContentGenerator, PostQueue
from scheduler import BlogScheduler


def print_banner():
    """Print bot banner"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║       BLACK CRAB PARK BLOG BOT                        ║
    ║       Automated Blogger Posting System                ║
    ╚═══════════════════════════════════════════════════════╝
    """)


def show_status(scheduler):
    """Display current bot status"""
    status = scheduler.get_status()
    print("\n📊 BOT STATUS")
    print("=" * 50)
    print(f"  Blog:            {BLOG_CONFIG['blog_name']}")
    print(f"  Blog URL:        {BLOG_CONFIG['blog_url']}")
    print(f"  Posting every:   {status['interval_days']} days")
    print()
    print(f"  Last post:       {status['last_post'] or 'Never'}")
    print(f"  Days since:      {status['days_since_last'] or 'N/A'}")
    print(f"  Next post due:   {status['next_post_due']}")
    print(f"  Ready to post:   {'YES' if status['should_post_now'] else 'No'}")
    print()
    print(f"  Total posts:     {status['post_count']}")
    print(f"  Queue size:      {status['queue_size']}")
    print()
    print("🤖 AI STATUS")
    print("-" * 50)
    print(f"  Ollama URL:      {AI_CONFIG['ollama_url']}")
    print(f"  Model:           {AI_CONFIG['model']}")
    print(f"  Available:       {'YES' if status['ollama_available'] else 'No (using templates)'}")
    print()
    print("📁 PATHS")
    print("-" * 50)
    print(f"  Drafts:          {PATHS['drafts_dir']}")
    print(f"  Posted logs:     {PATHS['posted_dir']}")
    print(f"  Scheduler logs:  {PATHS['logs_dir']}")


def setup_wizard():
    """Interactive setup wizard"""
    print("\n🔧 SETUP WIZARD")
    print("=" * 50)

    # Check Google API
    print("\n1. Checking Google API libraries...")
    if GOOGLE_API_AVAILABLE:
        print("   ✓ Google API libraries installed")
    else:
        print("   ✗ Missing libraries. Run:")
        print("     pip install google-api-python-client google-auth-oauthlib")

    # Check credentials
    print("\n2. Checking credentials...")
    creds_path = Path(BLOG_CONFIG.get("credentials_path", "credentials.json"))
    if creds_path.exists():
        print(f"   ✓ Found: {creds_path}")
    else:
        print(f"   ✗ Missing: {creds_path}")
        print("   Download from: Google Cloud Console > APIs & Services > Credentials")
        print("   Enable the Blogger API first!")

    # Check Blog ID
    print("\n3. Checking Blog ID...")
    if BLOG_CONFIG["blog_id"] != "YOUR_BLOG_ID_HERE":
        print(f"   ✓ Blog ID: {BLOG_CONFIG['blog_id']}")
    else:
        print("   ✗ Blog ID not set!")
        print("   Get it from: Blogger Dashboard > Settings > Blog ID")
        print("   Or from the URL: blogger.com/blog/posts/BLOG_ID")

    # Check Ollama
    print("\n4. Checking Ollama (optional)...")
    generator = ContentGenerator()
    if generator.check_ollama():
        print(f"   ✓ Ollama available at {AI_CONFIG['ollama_url']}")
    else:
        print(f"   ○ Ollama not available (will use templates)")
        print(f"     To enable AI: Install Ollama and run 'ollama pull {AI_CONFIG['model']}'")

    print("\n" + "=" * 50)
    print("Setup complete! Edit config.py to configure settings.")


def interactive_menu(scheduler):
    """Interactive command menu"""
    while True:
        print("\n" + "=" * 50)
        print("COMMANDS:")
        print("  1. Show status")
        print("  2. Generate preview (don't post)")
        print("  3. Post now (as draft)")
        print("  4. Post now (publish)")
        print("  5. Start scheduler daemon")
        print("  6. Show cron setup")
        print("  7. Setup wizard")
        print("  8. Test Blogger connection")
        print("  q. Quit")
        print("=" * 50)

        choice = input("\nChoice: ").strip().lower()

        if choice == '1':
            show_status(scheduler)

        elif choice == '2':
            print("\nGenerating preview...")
            post = scheduler.generator.generate_scheduled_post()
            print(f"\n📝 Title: {post['title']}")
            print(f"   Method: {post['method']}")
            print(f"\n{post['content']}")

        elif choice == '3':
            print("\nCreating draft...")
            topic = input("Topic (or Enter for auto): ").strip() or None
            result = scheduler.create_and_post(topic=topic, is_draft=True)
            if result["success"]:
                print(f"✓ Draft created: {result['post'].get('title')}")
            else:
                print(f"✗ Failed: {result.get('error')}")

        elif choice == '4':
            confirm = input("Publish immediately? (yes/no): ").strip().lower()
            if confirm == 'yes':
                topic = input("Topic (or Enter for auto): ").strip() or None
                result = scheduler.create_and_post(topic=topic, is_draft=False)
                if result["success"]:
                    print(f"✓ Published: {result['post'].get('title')}")
                    print(f"  URL: {result['post'].get('url', 'N/A')}")
                else:
                    print(f"✗ Failed: {result.get('error')}")
            else:
                print("Cancelled.")

        elif choice == '5':
            print("\nStarting scheduler daemon...")
            print("Press Ctrl+C to stop")
            scheduler.run_daemon()

        elif choice == '6':
            from scheduler import generate_cron_entry, generate_systemd_service
            print("\n--- CRON ENTRY ---")
            print(generate_cron_entry())
            print("\n--- SYSTEMD SERVICE ---")
            print(generate_systemd_service())

        elif choice == '7':
            setup_wizard()

        elif choice == '8':
            print("\nTesting Blogger connection...")
            try:
                client = get_client(use_mock=False)
                client.authenticate()
                info = client.get_blog_info()
                if info:
                    print(f"✓ Connected to: {info.get('name')}")
                    print(f"  URL: {info.get('url')}")
                    print(f"  Posts: {info.get('posts_count')}")
                else:
                    print("✗ Could not get blog info")
            except Exception as e:
                print(f"✗ Connection failed: {e}")

        elif choice == 'q':
            print("Goodbye!")
            break

        else:
            print("Invalid choice")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Black Crab Park Blog Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bot.py                     # Interactive mode
  python bot.py --status            # Show current status
  python bot.py --post              # Post immediately (as draft)
  python bot.py --post --publish    # Post and publish
  python bot.py --schedule          # Start scheduler daemon
  python bot.py --setup             # Run setup wizard
        """
    )

    parser.add_argument("--status", action="store_true", help="Show bot status")
    parser.add_argument("--post", action="store_true", help="Create a post now")
    parser.add_argument("--publish", action="store_true", help="Publish (not draft)")
    parser.add_argument("--topic", type=str, help="Post topic")
    parser.add_argument("--schedule", action="store_true", help="Start scheduler daemon")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--mock", action="store_true", help="Mock mode (no actual posting)")

    args = parser.parse_args()

    print_banner()

    scheduler = BlogScheduler(use_mock=args.mock)

    if args.setup:
        setup_wizard()
    elif args.status:
        show_status(scheduler)
    elif args.post:
        is_draft = not args.publish
        print(f"Creating {'draft' if is_draft else 'published post'}...")
        result = scheduler.create_and_post(topic=args.topic, is_draft=is_draft)
        if result["success"]:
            print(f"✓ Success: {result['post'].get('title')}")
            if not is_draft:
                print(f"  URL: {result['post'].get('url')}")
        else:
            print(f"✗ Failed: {result.get('error')}")
    elif args.schedule:
        print("Starting scheduler daemon...")
        print("Press Ctrl+C to stop")
        scheduler.run_daemon()
    else:
        # Interactive mode
        interactive_menu(scheduler)


if __name__ == "__main__":
    main()
