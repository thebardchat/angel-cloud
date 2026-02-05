import weaviate
import re
from pathlib import Path

def parse_rag_file(filepath):
    """Parse RAG.md into chunks by ## headers"""
    content = Path(filepath).read_text(encoding='utf-8')

    # Split by ## headers
    sections = re.split(r'\n## ', content)
    chunks = []

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split('\n')
        header = lines[0].replace('#', '').strip()
        body = '\n'.join(lines[1:]).strip()

        if not body:
            continue

        # Categorize based on header keywords
        header_lower = header.lower()
        if any(word in header_lower for word in ['family', 'sons', 'wife', 'tiffany']):
            category = 'family'
        elif any(word in header_lower for word in ['faith', 'god', 'christian']):
            category = 'faith'
        elif any(word in header_lower for word in ['technical', 'code', 'project', 'tools']):
            category = 'technical'
        elif any(word in header_lower for word in ['philosophy', 'message', 'mission']):
            category = 'philosophy'
        else:
            category = 'general'

        chunks.append({
            'content': f"## {header}\n{body}",
            'category': category,
            'source': 'RAG.md'
        })

    return chunks

def import_to_weaviate(chunks):
    """Import chunks into LegacyKnowledge class"""
    client = weaviate.Client("http://localhost:8080")

    if not client.is_ready():
        print("Error: Weaviate not ready")
        return

    imported = 0
    for chunk in chunks:
        try:
            client.data_object.create(
                data_object=chunk,
                class_name="LegacyKnowledge"
            )
            imported += 1
            print(f"✓ Imported: {chunk['category']} - {chunk['content'][:50]}...")
        except Exception as e:
            print(f"✗ Error importing chunk: {e}")

    print(f"\n=== Imported {imported}/{len(chunks)} chunks ===")

def verify_import():
    """Query to verify data was imported"""
    client = weaviate.Client("http://localhost:8080")

    result = client.query.aggregate("LegacyKnowledge").with_meta_count().do()
    count = result['data']['Aggregate']['LegacyKnowledge'][0]['meta']['count']
    print(f"\nTotal LegacyKnowledge records: {count}")

    # Show sample
    sample = client.query.get("LegacyKnowledge", ["content", "category"]).with_limit(2).do()
    print("\nSample records:")
    for item in sample['data']['Get']['LegacyKnowledge']:
        print(f"  [{item['category']}] {item['content'][:80]}...")

if __name__ == "__main__":
    import sys

    rag_path = sys.argv[1] if len(sys.argv) > 1 else "RAG.md"

    print(f"Parsing {rag_path}...")
    chunks = parse_rag_file(rag_path)
    print(f"Found {len(chunks)} chunks\n")

    print("Importing to Weaviate...")
    import_to_weaviate(chunks)

    print("\nVerifying import...")
    verify_import()
