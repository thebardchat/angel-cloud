#!/usr/bin/env python3
"""
Log conversations to Weaviate for ShaneBrain/Angel Cloud

Usage:
    # Log a single message
    python log_conversation.py "Hello world" --role user --mode logibot

    # View recent conversations
    python log_conversation.py --view

    # View by session
    python log_conversation.py --view --session abc123

    # Interactive logging mode
    python log_conversation.py --interactive
"""

import argparse
import sys
from weaviate_utils import (
    get_client,
    log_conversation,
    get_recent_conversations,
    get_now_iso
)


def display_conversations(convos):
    """Pretty print conversations"""
    if not convos:
        print("No conversations found.")
        return

    print(f"\n{'='*60}")
    print(f"Recent conversations ({len(convos)} results):")
    print('='*60)

    for convo in convos:
        role = convo.get('role', '?')
        mode = convo.get('mode', 'default')
        message = convo.get('message', '')
        timestamp = convo.get('timestamp', '')[:19]  # Trim to readable length
        session = convo.get('session_id', '')[:12]

        # Format role indicator
        role_icon = '👤' if role == 'user' else '🤖'

        print(f"\n{role_icon} [{mode}] {timestamp}")
        print(f"   Session: {session}")
        print(f"   {message[:200]}{'...' if len(message) > 200 else ''}")


def interactive_mode(client):
    """Interactive conversation logging"""
    import uuid as uuid_lib

    print("\n=== ShaneBrain Conversation Logger ===")
    print("Commands:")
    print("  /mode <name>   - Set mode (logibot, shanebrain, angel)")
    print("  /session       - Start new session")
    print("  /view          - View recent conversations")
    print("  /quit          - Exit")
    print("  <text>         - Log as user message")
    print("  ><text>        - Log as assistant message")
    print("-" * 40)

    current_mode = "logibot"
    current_session = f"session_{uuid_lib.uuid4().hex[:8]}"

    print(f"Session: {current_session}")
    print(f"Mode: {current_mode}")

    while True:
        try:
            user_input = input(f"[{current_mode}] > ").strip()

            if not user_input:
                continue

            if user_input == '/quit':
                print("Goodbye!")
                break

            elif user_input.startswith('/mode '):
                current_mode = user_input[6:].strip()
                print(f"Mode set to: {current_mode}")

            elif user_input == '/session':
                current_session = f"session_{uuid_lib.uuid4().hex[:8]}"
                print(f"New session: {current_session}")

            elif user_input == '/view':
                convos = get_recent_conversations(
                    client,
                    limit=10,
                    session_id=current_session
                )
                display_conversations(convos)

            elif user_input.startswith('>'):
                # Assistant message
                message = user_input[1:].strip()
                if message:
                    result = log_conversation(
                        client, message, "assistant",
                        mode=current_mode, session_id=current_session
                    )
                    if result:
                        print("✓ Logged assistant message")
                    else:
                        print("✗ Failed to log")

            else:
                # User message
                result = log_conversation(
                    client, user_input, "user",
                    mode=current_mode, session_id=current_session
                )
                if result:
                    print("✓ Logged user message")
                else:
                    print("✗ Failed to log")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Log and view ShaneBrain conversations in Weaviate"
    )
    parser.add_argument('message', nargs='?', help='Message to log')
    parser.add_argument('--role', '-r', default='user',
                        choices=['user', 'assistant'],
                        help='Message role (default: user)')
    parser.add_argument('--mode', '-m', default='logibot',
                        help='Chat mode (default: logibot)')
    parser.add_argument('--session', '-s', help='Session ID')
    parser.add_argument('--view', '-v', action='store_true',
                        help='View recent conversations')
    parser.add_argument('--limit', '-n', type=int, default=20,
                        help='Max results for view (default: 20)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive logging mode')

    args = parser.parse_args()

    client = get_client()
    if not client:
        print("Error: Cannot connect to Weaviate")
        sys.exit(1)

    if args.interactive:
        interactive_mode(client)
        return

    if args.view:
        convos = get_recent_conversations(
            client,
            limit=args.limit,
            mode=args.mode if args.mode != 'logibot' else None,
            session_id=args.session
        )
        display_conversations(convos)
        return

    if args.message:
        result = log_conversation(
            client,
            args.message,
            args.role,
            mode=args.mode,
            session_id=args.session
        )
        if result:
            print(f"✓ Logged {args.role} message to Weaviate")
            print(f"  UUID: {result}")
        else:
            print("✗ Failed to log message")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
