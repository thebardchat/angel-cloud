import weaviate
import time

def setup_schema():
    client = weaviate.Client("http://localhost:8080")

    # Wait for Weaviate to be ready
    for i in range(5):
        try:
            if client.is_ready():
                print("Weaviate is ready!")
                break
        except:
            print(f"Waiting for Weaviate... attempt {i+1}")
            time.sleep(3)

    # Define the schemas
    schemas = [
        {
            "class": "Conversation",
            "description": "Chat history for ShaneBrain and Angel Cloud",
            "vectorizer": "none",
            "properties": [
                {"name": "message", "dataType": ["text"]},
                {"name": "role", "dataType": ["string"]},
                {"name": "mode", "dataType": ["string"]},
                {"name": "timestamp", "dataType": ["date"]},
                {"name": "session_id", "dataType": ["string"]}
            ]
        },
        {
            "class": "LegacyKnowledge",
            "description": "Shane's RAG data and family legacy wisdom",
            "vectorizer": "none",
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "category", "dataType": ["string"]},
                {"name": "source", "dataType": ["string"]}
            ]
        },
        {
            "class": "CrisisLog",
            "description": "Logs for high-severity wellness detections",
            "vectorizer": "none",
            "properties": [
                {"name": "input_text", "dataType": ["text"]},
                {"name": "severity", "dataType": ["string"]},
                {"name": "timestamp", "dataType": ["date"]}
            ]
        },
        {
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
    ]

    for schema in schemas:
        try:
            client.schema.create_class(schema)
            print(f"✓ Created class: {schema['class']}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"○ Class {schema['class']} already exists - skipping")
            else:
                print(f"✗ Error creating {schema['class']}: {e}")

if __name__ == "__main__":
    setup_schema()
