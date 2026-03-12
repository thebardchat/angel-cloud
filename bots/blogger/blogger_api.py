"""
Blogger API Integration for Black Crab Park Blog

Handles authentication and posting to Google Blogger.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Warning: Google API libraries not installed. Run: pip install google-api-python-client google-auth-oauthlib")

from config import BLOG_CONFIG, GOOGLE_CONFIG, PATHS


class BloggerClient:
    """Client for interacting with Blogger API"""

    def __init__(self):
        self.service = None
        self.blog_id = BLOG_CONFIG["blog_id"]
        self.credentials = None

    def authenticate(self):
        """Authenticate with Google Blogger API"""
        if not GOOGLE_API_AVAILABLE:
            raise RuntimeError("Google API libraries not installed")

        creds = None
        token_path = Path(GOOGLE_CONFIG["token_path"])
        creds_path = Path(GOOGLE_CONFIG["credentials_path"])

        # Load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(token_path),
                GOOGLE_CONFIG["scopes"]
            )

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {creds_path}\n"
                        "Download from Google Cloud Console > APIs & Services > Credentials"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(creds_path),
                    GOOGLE_CONFIG["scopes"]
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build('blogger', 'v3', credentials=creds)
        print("Authenticated with Blogger API")
        return True

    def get_blog_info(self):
        """Get information about the blog"""
        if not self.service:
            self.authenticate()

        try:
            blog = self.service.blogs().get(blogId=self.blog_id).execute()
            return {
                "name": blog.get("name"),
                "url": blog.get("url"),
                "posts_count": blog.get("posts", {}).get("totalItems", 0),
                "updated": blog.get("updated")
            }
        except Exception as e:
            print(f"Error getting blog info: {e}")
            return None

    def create_post(self, title, content, labels=None, is_draft=False):
        """
        Create a new blog post

        Args:
            title: Post title
            content: HTML content of the post
            labels: List of labels/tags
            is_draft: If True, save as draft instead of publishing

        Returns:
            Post data dict or None on failure
        """
        if not self.service:
            self.authenticate()

        if labels is None:
            labels = BLOG_CONFIG["default_labels"]

        post_body = {
            "kind": "blogger#post",
            "blog": {"id": self.blog_id},
            "title": title,
            "content": content,
            "labels": labels
        }

        try:
            if is_draft or BLOG_CONFIG["draft_mode"]:
                # Create as draft
                post = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_body,
                    isDraft=True
                ).execute()
                print(f"Draft created: {post.get('title')}")
            else:
                # Publish immediately
                post = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_body,
                    isDraft=False
                ).execute()
                print(f"Published: {post.get('title')}")

            # Log the post
            self._log_post(post)
            return post

        except Exception as e:
            print(f"Error creating post: {e}")
            return None

    def get_recent_posts(self, max_results=10):
        """Get recent posts from the blog"""
        if not self.service:
            self.authenticate()

        try:
            posts = self.service.posts().list(
                blogId=self.blog_id,
                maxResults=max_results
            ).execute()
            return posts.get("items", [])
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []

    def _log_post(self, post):
        """Log posted content for records"""
        log_file = PATHS["posted_dir"] / f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
        with open(log_file, 'w') as f:
            json.dump({
                "id": post.get("id"),
                "title": post.get("title"),
                "url": post.get("url"),
                "published": post.get("published"),
                "labels": post.get("labels", [])
            }, f, indent=2)


class MockBloggerClient:
    """Mock client for testing without API access"""

    def __init__(self):
        self.blog_id = BLOG_CONFIG["blog_id"]

    def authenticate(self):
        print("[MOCK] Authenticated with Blogger API")
        return True

    def get_blog_info(self):
        return {
            "name": "Black Crab Park (Mock)",
            "url": BLOG_CONFIG["blog_url"],
            "posts_count": 42,
            "updated": datetime.now().isoformat()
        }

    def create_post(self, title, content, labels=None, is_draft=False):
        post_id = f"mock_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print(f"[MOCK] {'Draft' if is_draft else 'Published'}: {title}")

        # Save to drafts folder for review
        draft_file = PATHS["drafts_dir"] / f"{post_id}.html"
        with open(draft_file, 'w') as f:
            f.write(f"<h1>{title}</h1>\n{content}")
        print(f"[MOCK] Saved to: {draft_file}")

        return {
            "id": post_id,
            "title": title,
            "url": f"{BLOG_CONFIG['blog_url']}/mock/{post_id}",
            "published": datetime.now().isoformat(),
            "labels": labels or BLOG_CONFIG["default_labels"]
        }

    def get_recent_posts(self, max_results=10):
        return []


def get_client(use_mock=False):
    """Get appropriate Blogger client"""
    if use_mock or not GOOGLE_API_AVAILABLE:
        return MockBloggerClient()
    return BloggerClient()


if __name__ == "__main__":
    # Test the client
    client = get_client(use_mock=True)
    client.authenticate()

    info = client.get_blog_info()
    print(f"\nBlog Info: {info}")

    # Test post
    test_post = client.create_post(
        title="Test Post from Bot",
        content="<p>This is a test post from the Black Crab Park Bot!</p>",
        is_draft=True
    )
    print(f"\nTest post created: {test_post}")
