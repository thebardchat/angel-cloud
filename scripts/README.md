# ShaneBrain Weaviate Scripts

Python scripts for managing the Weaviate vector database used by ShaneBrain and Angel Cloud.

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Weaviate** (via Docker or START-SHANEBRAIN.bat):
   ```bash
   docker run -d -p 8080:8080 semitechnologies/weaviate:latest
   ```

## Quick Start

```bash
# 1. Set up the schema (creates Conversation, LegacyKnowledge, CrisisLog classes)
python scripts/setup_weaviate_schema.py

# 2. Import your RAG data
python scripts/import_rag_to_weaviate.py RAG.md

# 3. Verify everything is working
python scripts/verify_weaviate.py
```

## Scripts Reference

### setup_weaviate_schema.py
Creates the Weaviate schema classes:
- **Conversation**: Chat history (message, role, mode, timestamp, session_id)
- **LegacyKnowledge**: RAG data (content, category, source)
- **CrisisLog**: Wellness alerts (input_text, severity, timestamp)

```bash
python scripts/setup_weaviate_schema.py
```

### import_rag_to_weaviate.py
Parses a RAG.md file and imports chunks into LegacyKnowledge.
Auto-categorizes by header keywords (family, faith, technical, philosophy).

```bash
python scripts/import_rag_to_weaviate.py RAG.md
python scripts/import_rag_to_weaviate.py path/to/custom-rag.md
```

### verify_weaviate.py
Quick status check of Weaviate connection, schema, and record counts.

```bash
python scripts/verify_weaviate.py
```

### query_legacy.py
Interactive CLI to search LegacyKnowledge.

```bash
# Interactive mode
python scripts/query_legacy.py

# Direct search
python scripts/query_legacy.py "family values"

# Filter by category
python scripts/query_legacy.py --category faith

# List all categories
python scripts/query_legacy.py --list-categories
```

**Interactive commands**:
- `/cat <name>` - Filter by category
- `/cats` - List all categories
- `/all` - Show all records
- `/quit` - Exit
- `<text>` - Search for text

### log_conversation.py
Log and view chat conversations.

```bash
# Log a message
python scripts/log_conversation.py "Hello world" --role user --mode logibot

# View recent conversations
python scripts/log_conversation.py --view

# Interactive logging
python scripts/log_conversation.py --interactive
```

**Interactive commands**:
- `/mode <name>` - Set mode (logibot, shanebrain, angel)
- `/session` - Start new session
- `/view` - View recent conversations
- `/quit` - Exit
- `<text>` - Log as user message
- `><text>` - Log as assistant message

### log_crisis.py
Log and view wellness/crisis detection events.

```bash
# Log a crisis event
python scripts/log_crisis.py "concerning text" --severity high

# View crisis logs
python scripts/log_crisis.py --view

# Filter by severity
python scripts/log_crisis.py --view --severity critical

# Show statistics
python scripts/log_crisis.py --stats

# Export to file
python scripts/log_crisis.py --export report.txt
```

**Severity levels**: low, medium, high, critical

### weaviate_utils.py
Reusable helper module. Import in your own scripts:

```python
from scripts.weaviate_utils import (
    get_client,
    log_conversation,
    log_crisis,
    add_legacy_knowledge,
    search_legacy,
    get_recent_conversations,
)

# Connect
client = get_client()

# Log a chat message
log_conversation(client, "Hello!", "user", mode="logibot")

# Search knowledge
results = search_legacy(client, "family values", category="family")

# Log crisis event
log_crisis(client, "concerning input", severity="high")
```

## Integration with Node.js

To use from the Node.js Angel Cloud server, you can either:

1. **Call Python scripts via child_process**:
   ```javascript
   const { execSync } = require('child_process');
   const result = execSync('python scripts/query_legacy.py "search term"');
   ```

2. **Use the Weaviate JavaScript client** directly (see weaviate-integration.js)

## Weaviate REST API

You can also interact with Weaviate directly via REST:

```bash
# Check if ready
curl http://localhost:8080/v1/.well-known/ready

# Get schema
curl http://localhost:8080/v1/schema

# Query (GraphQL)
curl -X POST http://localhost:8080/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Get { LegacyKnowledge(limit: 5) { content category } } }"}'
```

## Troubleshooting

**"Weaviate not ready"**
- Make sure Weaviate is running: `docker ps | grep weaviate`
- Check it's on port 8080: `curl http://localhost:8080/v1/.well-known/ready`

**"Class already exists"**
- This is normal if re-running setup - schema won't be duplicated

**Import errors**
- Run setup_weaviate_schema.py first to create classes
- Check your RAG.md file has `## Headers` to split on
