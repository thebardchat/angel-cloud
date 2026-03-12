#!/usr/bin/env python3
"""
CLI tool to query LegacyKnowledge in Weaviate
Usage:
    python query_legacy.py                    # Interactive mode
    python query_legacy.py "search term"      # Direct search
    python query_legacy.py --category faith   # Filter by category
    python query_legacy.py --list-categories  # Show all categories
"""

import weaviate
import argparse
import sys

def get_client():
    """Create Weaviate client"""
    client = weaviate.Client("http://localhost:8080")
    if not client.is_ready():
        print("Error: Weaviate is not running. Start it first.")
        sys.exit(1)
    return client

def search_legacy(client, query=None, category=None, limit=10):
    """Search LegacyKnowledge by text or category"""
    try:
        q = client.query.get("LegacyKnowledge", ["content", "category", "source"])

        if category:
            q = q.with_where({
                "path": ["category"],
                "operator": "Equal",
                "valueString": category
            })

        if query:
            # Use BM25 search for text matching
            q = q.with_bm25(query=query, properties=["content"])

        q = q.with_limit(limit)
        result = q.do()

        records = result.get('data', {}).get('Get', {}).get('LegacyKnowledge', [])
        return records
    except Exception as e:
        print(f"Search error: {e}")
        return []

def list_categories(client):
    """Get all unique categories"""
    try:
        result = client.query.aggregate("LegacyKnowledge").with_group_by_filter(
            ["category"]
        ).with_fields("groupedBy { value } meta { count }").do()

        groups = result.get('data', {}).get('Aggregate', {}).get('LegacyKnowledge', [])
        return [(g['groupedBy']['value'], g['meta']['count']) for g in groups]
    except Exception as e:
        print(f"Error listing categories: {e}")
        return []

def display_results(records):
    """Pretty print search results"""
    if not records:
        print("No results found.")
        return

    print(f"\n{'='*60}")
    print(f"Found {len(records)} results:")
    print('='*60)

    for i, record in enumerate(records, 1):
        category = record.get('category', 'unknown')
        content = record.get('content', '')

        # Truncate long content for display
        if len(content) > 300:
            display_content = content[:300] + "..."
        else:
            display_content = content

        print(f"\n[{i}] Category: {category}")
        print("-" * 40)
        print(display_content)
        print()

def interactive_mode(client):
    """Run interactive query loop"""
    print("\n=== ShaneBrain Legacy Knowledge Query ===")
    print("Commands:")
    print("  /cat <name>  - Filter by category")
    print("  /cats        - List all categories")
    print("  /all         - Show all records (limit 20)")
    print("  /quit        - Exit")
    print("  <text>       - Search for text")
    print("-" * 40)

    current_category = None

    while True:
        try:
            prompt = f"[{current_category or 'all'}] > "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            if user_input == '/quit':
                print("Goodbye!")
                break

            elif user_input == '/cats':
                categories = list_categories(client)
                if categories:
                    print("\nCategories:")
                    for cat, count in categories:
                        print(f"  {cat}: {count} records")
                else:
                    print("No categories found.")

            elif user_input.startswith('/cat '):
                current_category = user_input[5:].strip() or None
                if current_category:
                    print(f"Filter set to: {current_category}")
                else:
                    print("Filter cleared.")

            elif user_input == '/all':
                results = search_legacy(client, category=current_category, limit=20)
                display_results(results)

            else:
                # Text search
                results = search_legacy(client, query=user_input, category=current_category)
                display_results(results)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break

def main():
    parser = argparse.ArgumentParser(
        description="Query ShaneBrain's Legacy Knowledge in Weaviate"
    )
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--category', '-c', help='Filter by category')
    parser.add_argument('--list-categories', '-l', action='store_true',
                        help='List all categories')
    parser.add_argument('--limit', '-n', type=int, default=10,
                        help='Max results to return (default: 10)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')

    args = parser.parse_args()

    client = get_client()

    if args.list_categories:
        categories = list_categories(client)
        if categories:
            print("Categories in LegacyKnowledge:")
            for cat, count in categories:
                print(f"  {cat}: {count} records")
        else:
            print("No categories found.")
        return

    if args.interactive or (not args.query and not args.category):
        interactive_mode(client)
        return

    # Direct query
    results = search_legacy(
        client,
        query=args.query,
        category=args.category,
        limit=args.limit
    )
    display_results(results)

if __name__ == "__main__":
    main()
