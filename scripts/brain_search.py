#!/usr/bin/env python3
"""
ShaneBrain Unified Search

Searches across all knowledge sources in Weaviate:
- LegacyKnowledge (RAG.md content)
- SessionMemory (consolidated session exports)
- Conversation (chat history)

Usage:
    python brain_search.py "family values"
    python brain_search.py "logibot dispatch" --source legacy
    python brain_search.py --interactive
"""

import argparse
import sys
from weaviate_utils import get_client


def search_legacy(client, query, limit=5):
    """Search LegacyKnowledge"""
    try:
        result = client.query.get(
            "LegacyKnowledge", ["content", "category", "source"]
        ).with_bm25(
            query=query, properties=["content"]
        ).with_limit(limit).do()

        records = result.get('data', {}).get('Get', {}).get('LegacyKnowledge', [])
        return [{'type': 'legacy', 'category': r.get('category'), **r} for r in records]
    except Exception:
        return []


def search_memory(client, query, limit=5):
    """Search SessionMemory"""
    try:
        result = client.query.get(
            "SessionMemory", ["content", "section", "session_file", "session_date"]
        ).with_bm25(
            query=query, properties=["content"]
        ).with_limit(limit).do()

        records = result.get('data', {}).get('Get', {}).get('SessionMemory', [])
        return [{'type': 'memory', **r} for r in records]
    except Exception:
        return []


def search_conversations(client, query, limit=5):
    """Search Conversation history"""
    try:
        result = client.query.get(
            "Conversation", ["message", "role", "mode", "timestamp"]
        ).with_bm25(
            query=query, properties=["message"]
        ).with_limit(limit).do()

        records = result.get('data', {}).get('Get', {}).get('Conversation', [])
        return [{'type': 'conversation', **r} for r in records]
    except Exception:
        return []


def unified_search(client, query, sources=None, limit=5):
    """
    Search across all knowledge sources

    Args:
        client: Weaviate client
        query: Search query
        sources: List of sources to search ('legacy', 'memory', 'conversation')
                 None = search all
        limit: Results per source
    """
    if sources is None:
        sources = ['legacy', 'memory', 'conversation']

    results = []

    if 'legacy' in sources:
        results.extend(search_legacy(client, query, limit))

    if 'memory' in sources:
        results.extend(search_memory(client, query, limit))

    if 'conversation' in sources:
        results.extend(search_conversations(client, query, limit))

    return results


def display_results(results):
    """Pretty print search results"""
    if not results:
        print("No results found.")
        return

    # Group by type
    by_type = {}
    for r in results:
        t = r.get('type', 'unknown')
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(r)

    type_icons = {
        'legacy': '📚',
        'memory': '🧠',
        'conversation': '💬'
    }

    type_names = {
        'legacy': 'Legacy Knowledge',
        'memory': 'Session Memory',
        'conversation': 'Conversation History'
    }

    for result_type, items in by_type.items():
        icon = type_icons.get(result_type, '📄')
        name = type_names.get(result_type, result_type)

        print(f"\n{icon} {name} ({len(items)} results)")
        print("=" * 50)

        for i, item in enumerate(items, 1):
            if result_type == 'legacy':
                cat = item.get('category', 'general')
                content = item.get('content', '')[:200]
                print(f"\n[{i}] Category: {cat}")
                print(f"    {content}...")

            elif result_type == 'memory':
                section = item.get('section', 'Unknown')
                file = item.get('session_file', '')
                content = item.get('content', '')[:200]
                print(f"\n[{i}] {section}")
                print(f"    File: {file}")
                print(f"    {content}...")

            elif result_type == 'conversation':
                role = item.get('role', '?')
                mode = item.get('mode', 'default')
                msg = item.get('message', '')[:150]
                timestamp = item.get('timestamp', '')[:19]
                icon = '👤' if role == 'user' else '🤖'
                print(f"\n[{i}] {icon} [{mode}] {timestamp}")
                print(f"    {msg}...")


def get_context_for_query(client, query, max_tokens=2000):
    """
    Get relevant context for a query, formatted for LLM consumption

    Returns a string with relevant knowledge that can be injected into prompts
    """
    results = unified_search(client, query, limit=3)

    if not results:
        return ""

    context_parts = []
    estimated_tokens = 0

    for r in results:
        if r['type'] == 'legacy':
            content = r.get('content', '')
            chunk = f"[Knowledge - {r.get('category', 'general')}]\n{content}\n"
        elif r['type'] == 'memory':
            content = r.get('content', '')
            chunk = f"[Session Memory - {r.get('section', '')}]\n{content}\n"
        elif r['type'] == 'conversation':
            msg = r.get('message', '')
            role = r.get('role', 'user')
            chunk = f"[Previous {role} message]\n{msg}\n"
        else:
            continue

        # Rough token estimate (4 chars per token)
        chunk_tokens = len(chunk) // 4
        if estimated_tokens + chunk_tokens > max_tokens:
            break

        context_parts.append(chunk)
        estimated_tokens += chunk_tokens

    return "\n---\n".join(context_parts)


def interactive_mode(client):
    """Interactive search mode"""
    print("\n=== ShaneBrain Unified Search ===")
    print("Commands:")
    print("  /legacy    - Search only legacy knowledge")
    print("  /memory    - Search only session memory")
    print("  /chat      - Search only conversations")
    print("  /all       - Search all sources (default)")
    print("  /context   - Get LLM-ready context for query")
    print("  /quit      - Exit")
    print("-" * 40)

    current_sources = None  # None = all

    while True:
        try:
            prompt = input("\n🔍 > ").strip()

            if not prompt:
                continue

            if prompt == '/quit':
                print("Goodbye!")
                break

            elif prompt == '/legacy':
                current_sources = ['legacy']
                print("Source filter: Legacy Knowledge only")
                continue

            elif prompt == '/memory':
                current_sources = ['memory']
                print("Source filter: Session Memory only")
                continue

            elif prompt == '/chat':
                current_sources = ['conversation']
                print("Source filter: Conversations only")
                continue

            elif prompt == '/all':
                current_sources = None
                print("Source filter: All sources")
                continue

            elif prompt.startswith('/context '):
                query = prompt[9:].strip()
                if query:
                    context = get_context_for_query(client, query)
                    print("\n--- Context for LLM ---")
                    print(context if context else "(no relevant context found)")
                continue

            # Regular search
            results = unified_search(client, prompt, sources=current_sources)
            display_results(results)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="ShaneBrain Unified Search across all knowledge sources"
    )
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--source', '-s', choices=['legacy', 'memory', 'conversation', 'all'],
                        default='all', help='Source to search (default: all)')
    parser.add_argument('--limit', '-n', type=int, default=5,
                        help='Max results per source (default: 5)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive search mode')
    parser.add_argument('--context', '-c', action='store_true',
                        help='Output LLM-ready context instead of formatted results')

    args = parser.parse_args()

    client = get_client()
    if not client:
        print("Error: Cannot connect to Weaviate")
        sys.exit(1)

    if args.interactive:
        interactive_mode(client)
        return

    if not args.query:
        parser.print_help()
        return

    sources = None if args.source == 'all' else [args.source]

    if args.context:
        context = get_context_for_query(client, args.query)
        print(context if context else "(no relevant context found)")
    else:
        results = unified_search(client, args.query, sources=sources, limit=args.limit)
        display_results(results)


if __name__ == "__main__":
    main()
