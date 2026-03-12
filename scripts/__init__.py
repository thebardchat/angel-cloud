# ShaneBrain Weaviate Scripts
# Import key utilities for easy access

from .weaviate_utils import (
    get_client,
    log_conversation,
    log_crisis,
    add_legacy_knowledge,
    search_legacy,
    get_recent_conversations,
    get_class_count,
    get_now_iso,
)

__all__ = [
    'get_client',
    'log_conversation',
    'log_crisis',
    'add_legacy_knowledge',
    'search_legacy',
    'get_recent_conversations',
    'get_class_count',
    'get_now_iso',
]
