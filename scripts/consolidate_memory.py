#!/usr/bin/env python3
"""
Consolidate memory exports into Weaviate

Parses session memory files from memory-exports/ and imports them
into Weaviate for searchable context retrieval.

Usage:
    python consolidate_memory.py                    # Process all memory files
    python consolidate_memory.py --recent 10        # Process last 10 files
    python consolidate_memory.py --file Session_2025-08-12_05-03.md
"""

import weaviate
import re
import argparse
from pathlib import Path
from datetime import datetime
from weaviate_utils import get_client, get_now_iso


def setup_memory_schema(client):
    """Create SessionMemory class if it doesn't exist"""
    schema = {
        "class": "SessionMemory",
        "description": "Consolidated session memories from Angel Cloud",
        "vectorizer": "none",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "session_date", "dataType": ["date"]},
            {"name": "session_file", "dataType": ["string"]},
            {"name": "section", "dataType": ["string"]},
            {"name": "imported_at", "dataType": ["date"]}
        ]
    }

    try:
        client.schema.create_class(schema)
        print("Created SessionMemory class")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("SessionMemory class already exists")
        else:
            print(f"Error creating schema: {e}")


def parse_session_file(filepath):
    """Parse a session memory markdown file into chunks"""
    content = Path(filepath).read_text(encoding='utf-8')
    filename = Path(filepath).name

    # Extract date from filename (Session_2025-08-12_05-03.md)
    date_match = re.search(r'Session_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', filename)
    if date_match:
        date_str = date_match.group(1)
        time_str = date_match.group(2).replace('-', ':')
        session_date = f"{date_str}T{time_str}:00Z"
    else:
        session_date = get_now_iso()

    chunks = []

    # Split by ## headers
    sections = re.split(r'\n## ', content)

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split('\n')
        header = lines[0].replace('#', '').strip()
        body = '\n'.join(lines[1:]).strip()

        if not body or len(body) < 20:
            continue

        # Clean up the content
        body = re.sub(r'\*\*', '', body)  # Remove bold markers
        body = re.sub(r'\n+', '\n', body)  # Collapse multiple newlines

        chunks.append({
            'content': body,
            'session_date': session_date,
            'session_file': filename,
            'section': header[:100],
            'imported_at': get_now_iso()
        })

    return chunks


def import_to_weaviate(client, chunks, skip_duplicates=True):
    """Import memory chunks to Weaviate"""
    imported = 0
    skipped = 0

    for chunk in chunks:
        # Check for duplicates by session_file and section
        if skip_duplicates:
            try:
                result = client.query.get(
                    "SessionMemory", ["session_file", "section"]
                ).with_where({
                    "operator": "And",
                    "operands": [
                        {"path": ["session_file"], "operator": "Equal", "valueString": chunk['session_file']},
                        {"path": ["section"], "operator": "Equal", "valueString": chunk['section']}
                    ]
                }).with_limit(1).do()

                existing = result.get('data', {}).get('Get', {}).get('SessionMemory', [])
                if existing:
                    skipped += 1
                    continue
            except Exception:
                pass

        try:
            client.data_object.create(
                data_object=chunk,
                class_name="SessionMemory"
            )
            imported += 1
            print(f"  + {chunk['section'][:50]}...")
        except Exception as e:
            print(f"  ! Error: {e}")

    return imported, skipped


def get_memory_files(memory_dir, recent=None):
    """Get list of memory files to process"""
    memory_path = Path(memory_dir)

    if not memory_path.exists():
        print(f"Memory directory not found: {memory_dir}")
        return []

    # Get all session files (exclude CURRENT_SESSION_FOCUS.md)
    files = sorted([
        f for f in memory_path.glob("Session_*.md")
    ], key=lambda x: x.stat().st_mtime, reverse=True)

    if recent:
        files = files[:recent]

    return files


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate memory exports into Weaviate"
    )
    parser.add_argument('--dir', '-d', default='memory-exports',
                        help='Memory exports directory (default: memory-exports)')
    parser.add_argument('--recent', '-r', type=int,
                        help='Only process N most recent files')
    parser.add_argument('--file', '-f',
                        help='Process a specific file')
    parser.add_argument('--no-skip', action='store_true',
                        help='Dont skip duplicate entries')

    args = parser.parse_args()

    # Connect to Weaviate
    client = get_client()
    if not client:
        print("Failed to connect to Weaviate")
        return

    # Setup schema
    setup_memory_schema(client)

    # Get files to process
    if args.file:
        files = [Path(args.dir) / args.file]
        if not files[0].exists():
            files = [Path(args.file)]
    else:
        files = get_memory_files(args.dir, args.recent)

    if not files:
        print("No memory files found")
        return

    print(f"\nProcessing {len(files)} memory files...")

    total_imported = 0
    total_skipped = 0

    for filepath in files:
        if not filepath.exists():
            print(f"File not found: {filepath}")
            continue

        print(f"\n[{filepath.name}]")
        chunks = parse_session_file(filepath)

        if not chunks:
            print("  (no content)")
            continue

        imported, skipped = import_to_weaviate(
            client, chunks,
            skip_duplicates=not args.no_skip
        )
        total_imported += imported
        total_skipped += skipped

    print(f"\n{'='*40}")
    print(f"Imported: {total_imported} chunks")
    print(f"Skipped:  {total_skipped} duplicates")

    # Show total count
    try:
        result = client.query.aggregate("SessionMemory").with_meta_count().do()
        count = result['data']['Aggregate']['SessionMemory'][0]['meta']['count']
        print(f"Total SessionMemory records: {count}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
