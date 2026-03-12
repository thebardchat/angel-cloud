"""
Black Crab Park Blog Bot Configuration
"""

import os
from pathlib import Path

# Blog Configuration
BLOG_CONFIG = {
    "blog_name": "Black Crab Park",
    "blog_id": os.getenv("BLOGGER_BLOG_ID", "YOUR_BLOG_ID_HERE"),  # Get from Blogger dashboard
    "blog_url": "https://blackcrabpark.blogspot.com",  # Update with actual URL

    # Posting schedule
    "post_interval_days": 3,
    "post_time": "09:00",  # 9 AM local time

    # Content settings
    "default_labels": ["Black Crab Park", "Blog", "Update"],
    "draft_mode": False,  # Set True to create drafts instead of publishing
}

# Google API Configuration
GOOGLE_CONFIG = {
    "credentials_path": os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
    "token_path": os.getenv("BLOGGER_TOKEN_PATH", "blogger_token.json"),
    "scopes": ["https://www.googleapis.com/auth/blogger"],
}

# Local AI Configuration (Ollama on Pi 5)
AI_CONFIG = {
    "enabled": True,
    "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
    "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
    "fallback_to_templates": True,  # Use templates if AI unavailable
}

# Content Templates (fallback when AI is unavailable)
CONTENT_TEMPLATES = {
    "greeting": [
        "Hello Black Crab Park family!",
        "Greetings from the Park!",
        "Welcome back to Black Crab Park!",
    ],
    "topics": [
        "community updates",
        "park improvements",
        "upcoming events",
        "neighborhood news",
        "seasonal changes",
        "wildlife sightings",
        "maintenance updates",
    ],
    "closing": [
        "Stay safe and see you around the park!",
        "Until next time, happy trails!",
        "Keep our community strong!",
    ],
}

# File paths
PATHS = {
    "base_dir": Path(__file__).parent,
    "logs_dir": Path(__file__).parent / "logs",
    "drafts_dir": Path(__file__).parent / "drafts",
    "posted_dir": Path(__file__).parent / "posted",
    "queue_file": Path(__file__).parent / "post_queue.json",
}

# Create directories
for path in [PATHS["logs_dir"], PATHS["drafts_dir"], PATHS["posted_dir"]]:
    path.mkdir(exist_ok=True)

# Bot personality (for AI-generated content)
BOT_PERSONALITY = """
You are the friendly voice of Black Crab Park, a community blog.
Your tone is:
- Warm and welcoming
- Community-focused
- Informative but casual
- Positive and encouraging

You write blog posts about park life, community events, neighborhood updates,
and things happening around Black Crab Park. Keep posts between 200-500 words.
Always end with a friendly sign-off.
"""
