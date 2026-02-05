"""
Weaviate utility functions for ShaneBrain/Angel Cloud
Reusable helpers for connecting and querying Weaviate
"""

import weaviate
from datetime import datetime, timezone
import time
import sys

# Default Weaviate connection
WEAVIATE_URL = "http://localhost:8080"


def get_client(url=WEAVIATE_URL, wait=True, max_retries=5):
    """
    Get a Weaviate client connection.

    Args:
        url: Weaviate server URL
        wait: If True, wait for Weaviate to be ready
        max_retries: Max connection attempts if wait=True

    Returns:
        weaviate.Client or None if connection fails
    """
    client = weaviate.Client(url)

    if wait:
        for i in range(max_retries):
            try:
                if client.is_ready():
                    return client
            except Exception:
                pass
            print(f"Waiting for Weaviate... attempt {i+1}/{max_retries}")
            time.sleep(3)
        print("Error: Could not connect to Weaviate")
        return None

    return client if client.is_ready() else None


def get_now_iso():
    """Get current timestamp in ISO 8601 format for Weaviate date fields"""
    return datetime.now(timezone.utc).isoformat()


def log_conversation(client, message, role, mode="default", session_id=None):
    """
    Log a conversation message to Weaviate.

    Args:
        client: Weaviate client
        message: The message text
        role: 'user' or 'assistant'
        mode: Chat mode (e.g., 'logibot', 'shanebrain', 'angel')
        session_id: Optional session identifier

    Returns:
        UUID of created object or None
    """
    try:
        obj = {
            "message": message,
            "role": role,
            "mode": mode,
            "timestamp": get_now_iso(),
            "session_id": session_id or f"session_{int(time.time())}"
        }
        uuid = client.data_object.create(
            data_object=obj,
            class_name="Conversation"
        )
        return uuid
    except Exception as e:
        print(f"Error logging conversation: {e}")
        return None


def log_crisis(client, input_text, severity="medium"):
    """
    Log a crisis detection event.

    Args:
        client: Weaviate client
        input_text: The text that triggered the detection
        severity: 'low', 'medium', 'high', 'critical'

    Returns:
        UUID of created object or None
    """
    valid_severities = ['low', 'medium', 'high', 'critical']
    if severity not in valid_severities:
        severity = 'medium'

    try:
        obj = {
            "input_text": input_text,
            "severity": severity,
            "timestamp": get_now_iso()
        }
        uuid = client.data_object.create(
            data_object=obj,
            class_name="CrisisLog"
        )
        return uuid
    except Exception as e:
        print(f"Error logging crisis: {e}")
        return None


def add_legacy_knowledge(client, content, category="general", source="manual"):
    """
    Add knowledge to LegacyKnowledge collection.

    Args:
        client: Weaviate client
        content: The knowledge content
        category: Category (family, faith, technical, philosophy, general)
        source: Source identifier

    Returns:
        UUID of created object or None
    """
    try:
        obj = {
            "content": content,
            "category": category,
            "source": source
        }
        uuid = client.data_object.create(
            data_object=obj,
            class_name="LegacyKnowledge"
        )
        return uuid
    except Exception as e:
        print(f"Error adding knowledge: {e}")
        return None


def search_legacy(client, query=None, category=None, limit=10):
    """
    Search LegacyKnowledge collection.

    Args:
        client: Weaviate client
        query: Text to search for (uses BM25)
        category: Filter by category
        limit: Max results

    Returns:
        List of matching records
    """
    try:
        q = client.query.get("LegacyKnowledge", ["content", "category", "source"])

        if category:
            q = q.with_where({
                "path": ["category"],
                "operator": "Equal",
                "valueString": category
            })

        if query:
            q = q.with_bm25(query=query, properties=["content"])

        q = q.with_limit(limit)
        result = q.do()

        return result.get('data', {}).get('Get', {}).get('LegacyKnowledge', [])
    except Exception as e:
        print(f"Search error: {e}")
        return []


def get_recent_conversations(client, limit=20, mode=None, session_id=None):
    """
    Get recent conversation history.

    Args:
        client: Weaviate client
        limit: Max results
        mode: Filter by mode
        session_id: Filter by session

    Returns:
        List of conversation records
    """
    try:
        q = client.query.get(
            "Conversation",
            ["message", "role", "mode", "timestamp", "session_id"]
        )

        # Build where filter
        filters = []
        if mode:
            filters.append({
                "path": ["mode"],
                "operator": "Equal",
                "valueString": mode
            })
        if session_id:
            filters.append({
                "path": ["session_id"],
                "operator": "Equal",
                "valueString": session_id
            })

        if len(filters) == 1:
            q = q.with_where(filters[0])
        elif len(filters) > 1:
            q = q.with_where({
                "operator": "And",
                "operands": filters
            })

        # Sort by timestamp descending
        q = q.with_sort([{"path": ["timestamp"], "order": "desc"}])
        q = q.with_limit(limit)

        result = q.do()
        return result.get('data', {}).get('Get', {}).get('Conversation', [])
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return []


def get_class_count(client, class_name):
    """Get total record count for a class"""
    try:
        result = client.query.aggregate(class_name).with_meta_count().do()
        return result['data']['Aggregate'][class_name][0]['meta']['count']
    except Exception:
        return 0


def delete_class_data(client, class_name):
    """Delete all objects in a class (use with caution!)"""
    try:
        client.batch.delete_objects(
            class_name=class_name,
            where={"path": ["_id"], "operator": "Like", "valueString": "*"}
        )
        print(f"Deleted all data from {class_name}")
        return True
    except Exception as e:
        print(f"Error deleting data: {e}")
        return False


# Quick test when run directly
if __name__ == "__main__":
    print("Testing Weaviate connection...")
    client = get_client(wait=True)

    if client:
        print("✓ Connected to Weaviate")
        print(f"\nClass counts:")
        for cls in ['Conversation', 'LegacyKnowledge', 'CrisisLog']:
            count = get_class_count(client, cls)
            print(f"  {cls}: {count}")
    else:
        print("✗ Failed to connect")
        sys.exit(1)
