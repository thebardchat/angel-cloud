import weaviate

def verify():
    client = weaviate.Client("http://localhost:8080")

    print("=== Weaviate Status ===")
    print(f"Ready: {client.is_ready()}")

    print("\n=== Schema Classes ===")
    schema = client.schema.get()
    for cls in schema.get('classes', []):
        print(f"  • {cls['class']}: {len(cls.get('properties', []))} properties")

    print("\n=== Record Counts ===")
    for class_name in ['Conversation', 'LegacyKnowledge', 'CrisisLog', 'SessionMemory']:
        try:
            result = client.query.aggregate(class_name).with_meta_count().do()
            count = result['data']['Aggregate'][class_name][0]['meta']['count']
            print(f"  {class_name}: {count} records")
        except:
            print(f"  {class_name}: not found or empty")

if __name__ == "__main__":
    verify()
