"""
Content Generator for Black Crab Park Blog

Generates blog post content using local Ollama LLM or template fallback.
"""

import random
import json
from datetime import datetime
from typing import Optional, Dict

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from config import AI_CONFIG, CONTENT_TEMPLATES, BOT_PERSONALITY


class ContentGenerator:
    """Generate blog post content"""

    def __init__(self):
        self.ollama_url = AI_CONFIG["ollama_url"]
        self.model = AI_CONFIG["model"]
        self.ai_enabled = AI_CONFIG["enabled"]

    def check_ollama(self) -> bool:
        """Check if Ollama is available"""
        if not REQUESTS_AVAILABLE or not self.ai_enabled:
            return False

        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def generate_with_ollama(self, prompt: str) -> Optional[str]:
        """Generate content using local Ollama"""
        if not self.check_ollama():
            return None

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 800
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Ollama error: {e}")

        return None

    def generate_from_template(self, topic: Optional[str] = None) -> Dict[str, str]:
        """Generate content from templates (fallback)"""
        if topic is None:
            topic = random.choice(CONTENT_TEMPLATES["topics"])

        greeting = random.choice(CONTENT_TEMPLATES["greeting"])
        closing = random.choice(CONTENT_TEMPLATES["closing"])

        # Generate a simple post
        date_str = datetime.now().strftime("%B %d, %Y")

        content = f"""
<p>{greeting}</p>

<p>Today we're sharing some thoughts about <strong>{topic}</strong> here at Black Crab Park.</p>

<p>As we move through {datetime.now().strftime("%B")}, there's always something happening in our little corner of the world. Whether it's the changing seasons, community gatherings, or just the everyday moments that make our neighborhood special, we're here to keep you connected.</p>

<p>We encourage everyone to get out and enjoy what our community has to offer. Take a walk through the park, say hello to your neighbors, and remember that we're all in this together.</p>

<p>{closing}</p>

<p><em>Posted on {date_str}</em></p>
"""

        title = f"Black Crab Park Update: {topic.title()}"

        return {
            "title": title,
            "content": content.strip(),
            "topic": topic,
            "method": "template"
        }

    def generate_post(self, topic: Optional[str] = None, custom_prompt: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a blog post

        Args:
            topic: Optional topic to write about
            custom_prompt: Optional custom prompt for AI generation

        Returns:
            Dict with title, content, topic, method
        """
        # Try AI generation first
        if self.ai_enabled:
            if custom_prompt:
                prompt = custom_prompt
            else:
                if topic is None:
                    topic = random.choice(CONTENT_TEMPLATES["topics"])

                prompt = f"""{BOT_PERSONALITY}

Write a blog post for Black Crab Park about: {topic}

The post should:
- Have an engaging title (on its own line, starting with "TITLE: ")
- Be 200-400 words
- Be warm and community-focused
- Include a greeting and closing
- Be formatted in simple HTML with <p> tags

Today's date is {datetime.now().strftime("%B %d, %Y")}.

Write the blog post now:"""

            ai_content = self.generate_with_ollama(prompt)

            if ai_content:
                # Parse title from AI response
                lines = ai_content.split('\n')
                title = f"Black Crab Park: {topic.title() if topic else 'Community Update'}"

                for line in lines:
                    if line.strip().upper().startswith("TITLE:"):
                        title = line.split(":", 1)[1].strip()
                        ai_content = '\n'.join(lines[lines.index(line)+1:])
                        break

                # Ensure HTML formatting
                if '<p>' not in ai_content:
                    paragraphs = ai_content.split('\n\n')
                    ai_content = '\n'.join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())

                return {
                    "title": title,
                    "content": ai_content,
                    "topic": topic,
                    "method": "ollama"
                }

        # Fallback to templates
        if AI_CONFIG["fallback_to_templates"]:
            return self.generate_from_template(topic)

        return {
            "title": "Black Crab Park Update",
            "content": "<p>Stay tuned for updates from Black Crab Park!</p>",
            "topic": topic,
            "method": "fallback"
        }

    def generate_scheduled_post(self) -> Dict[str, str]:
        """Generate a post for scheduled publishing"""
        # Rotate through topics
        topics = CONTENT_TEMPLATES["topics"]
        day_of_year = datetime.now().timetuple().tm_yday
        topic_index = (day_of_year // 3) % len(topics)  # Rotate every 3 days
        topic = topics[topic_index]

        return self.generate_post(topic=topic)


class PostQueue:
    """Manage a queue of posts to be published"""

    def __init__(self, queue_file):
        self.queue_file = queue_file
        self.queue = self._load_queue()

    def _load_queue(self) -> list:
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_queue(self):
        """Save queue to file"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f, indent=2)

    def add(self, post: Dict):
        """Add post to queue"""
        post['queued_at'] = datetime.now().isoformat()
        post['status'] = 'queued'
        self.queue.append(post)
        self._save_queue()

    def get_next(self) -> Optional[Dict]:
        """Get next post from queue"""
        for post in self.queue:
            if post.get('status') == 'queued':
                return post
        return None

    def mark_posted(self, post: Dict):
        """Mark post as published"""
        for p in self.queue:
            if p.get('queued_at') == post.get('queued_at'):
                p['status'] = 'posted'
                p['posted_at'] = datetime.now().isoformat()
                break
        self._save_queue()

    def get_pending_count(self) -> int:
        """Get count of queued posts"""
        return len([p for p in self.queue if p.get('status') == 'queued'])


if __name__ == "__main__":
    # Test content generation
    generator = ContentGenerator()

    print("=== Testing Content Generator ===\n")

    print(f"Ollama available: {generator.check_ollama()}")

    print("\n--- Generating post ---")
    post = generator.generate_post(topic="community events")

    print(f"\nTitle: {post['title']}")
    print(f"Method: {post['method']}")
    print(f"\nContent:\n{post['content'][:500]}...")
