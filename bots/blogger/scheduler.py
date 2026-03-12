"""
Post Scheduler for Black Crab Park Blog Bot

Handles scheduled posting every 3 days.
Can run as:
1. Daemon with APScheduler
2. Cron job (one-shot mode)
3. Systemd service
"""

import os
import sys
import json
import time
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config import BLOG_CONFIG, PATHS
from blogger_api import get_client
from content_generator import ContentGenerator, PostQueue

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PATHS["logs_dir"] / "scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BlogScheduler:
    """Scheduler for automated blog posting"""

    def __init__(self, use_mock=False):
        self.blogger = get_client(use_mock=use_mock)
        self.generator = ContentGenerator()
        self.queue = PostQueue(PATHS["queue_file"])
        self.state_file = PATHS["base_dir"] / "scheduler_state.json"
        self.running = False

    def _load_state(self) -> dict:
        """Load scheduler state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_post": None, "post_count": 0}

    def _save_state(self, state: dict):
        """Save scheduler state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def should_post_today(self) -> bool:
        """Check if we should post today based on 3-day interval"""
        state = self._load_state()
        last_post = state.get("last_post")

        if last_post is None:
            return True

        try:
            last_date = datetime.fromisoformat(last_post)
            days_since = (datetime.now() - last_date).days
            return days_since >= BLOG_CONFIG["post_interval_days"]
        except Exception:
            return True

    def create_and_post(self, topic: str = None, is_draft: bool = False) -> dict:
        """Generate and post content"""
        logger.info(f"Generating post (topic: {topic or 'auto'})")

        # Generate content
        if topic:
            post_data = self.generator.generate_post(topic=topic)
        else:
            post_data = self.generator.generate_scheduled_post()

        logger.info(f"Generated: {post_data['title']} (via {post_data['method']})")

        # Authenticate and post
        try:
            self.blogger.authenticate()
            result = self.blogger.create_post(
                title=post_data["title"],
                content=post_data["content"],
                is_draft=is_draft
            )

            if result:
                # Update state
                state = self._load_state()
                state["last_post"] = datetime.now().isoformat()
                state["post_count"] = state.get("post_count", 0) + 1
                self._save_state(state)

                logger.info(f"Posted successfully: {result.get('url', 'N/A')}")
                return {"success": True, "post": result, "content": post_data}

        except Exception as e:
            logger.error(f"Failed to post: {e}")

        return {"success": False, "error": str(e) if 'e' in dir() else "Unknown error"}

    def check_and_post(self):
        """Check if it's time to post and do so"""
        if not self.should_post_today():
            state = self._load_state()
            last = state.get("last_post", "never")
            logger.info(f"Not time to post yet. Last post: {last}")
            return False

        logger.info("Time to post! Starting scheduled post...")
        result = self.create_and_post()
        return result.get("success", False)

    def run_daemon(self, check_interval_hours: int = 1):
        """Run as a daemon, checking periodically"""
        logger.info(f"Starting scheduler daemon (check every {check_interval_hours}h)")
        self.running = True

        def handle_signal(signum, frame):
            logger.info("Received shutdown signal")
            self.running = False

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

        while self.running:
            try:
                self.check_and_post()
            except Exception as e:
                logger.error(f"Error in daemon loop: {e}")

            # Sleep until next check
            for _ in range(check_interval_hours * 60):  # Check every minute for shutdown
                if not self.running:
                    break
                time.sleep(60)

        logger.info("Scheduler daemon stopped")

    def get_status(self) -> dict:
        """Get scheduler status"""
        state = self._load_state()
        last_post = state.get("last_post")

        if last_post:
            last_date = datetime.fromisoformat(last_post)
            days_since = (datetime.now() - last_date).days
            next_post = last_date + timedelta(days=BLOG_CONFIG["post_interval_days"])
        else:
            days_since = None
            next_post = datetime.now()

        return {
            "last_post": last_post,
            "days_since_last": days_since,
            "next_post_due": next_post.isoformat() if next_post else None,
            "should_post_now": self.should_post_today(),
            "post_count": state.get("post_count", 0),
            "queue_size": self.queue.get_pending_count(),
            "interval_days": BLOG_CONFIG["post_interval_days"],
            "ollama_available": self.generator.check_ollama()
        }


def generate_cron_entry():
    """Generate cron entry for running every 3 days at 9 AM"""
    script_path = Path(__file__).resolve()
    python_path = sys.executable

    # Run at 9:00 AM on days 1, 4, 7, 10, 13, 16, 19, 22, 25, 28 of each month
    # This approximates "every 3 days"
    cron_line = f"0 9 */3 * * cd {script_path.parent} && {python_path} {script_path} --once"

    return f"""
# Black Crab Park Blog Bot - Posts every 3 days at 9 AM
# Add to crontab with: crontab -e
{cron_line}
"""


def generate_systemd_service():
    """Generate systemd service file"""
    script_path = Path(__file__).resolve()
    python_path = sys.executable

    return f"""[Unit]
Description=Black Crab Park Blog Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'pi')}
WorkingDirectory={script_path.parent}
ExecStart={python_path} {script_path} --daemon
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target

# Save as: /etc/systemd/system/blackcrab-blogger.service
# Enable with: sudo systemctl enable blackcrab-blogger
# Start with: sudo systemctl start blackcrab-blogger
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Black Crab Park Blog Scheduler")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for cron)")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    parser.add_argument("--post-now", action="store_true", help="Force post immediately")
    parser.add_argument("--draft", action="store_true", help="Create draft instead of publishing")
    parser.add_argument("--topic", type=str, help="Specific topic to write about")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no actual posting)")
    parser.add_argument("--cron", action="store_true", help="Show cron entry")
    parser.add_argument("--systemd", action="store_true", help="Show systemd service file")

    args = parser.parse_args()

    if args.cron:
        print(generate_cron_entry())
        sys.exit(0)

    if args.systemd:
        print(generate_systemd_service())
        sys.exit(0)

    scheduler = BlogScheduler(use_mock=args.mock)

    if args.status:
        status = scheduler.get_status()
        print("\n=== Black Crab Park Blog Scheduler ===")
        print(f"Last post:        {status['last_post'] or 'Never'}")
        print(f"Days since:       {status['days_since_last'] or 'N/A'}")
        print(f"Next post due:    {status['next_post_due']}")
        print(f"Should post now:  {status['should_post_now']}")
        print(f"Total posts:      {status['post_count']}")
        print(f"Queue size:       {status['queue_size']}")
        print(f"Posting interval: Every {status['interval_days']} days")
        print(f"Ollama available: {status['ollama_available']}")

    elif args.post_now:
        print("Forcing immediate post...")
        result = scheduler.create_and_post(topic=args.topic, is_draft=args.draft)
        if result["success"]:
            print(f"Success! Post: {result['post'].get('title')}")
        else:
            print(f"Failed: {result.get('error')}")

    elif args.once:
        # Cron mode - check and post if needed
        scheduler.check_and_post()

    elif args.daemon:
        # Daemon mode
        scheduler.run_daemon(check_interval_hours=1)

    else:
        parser.print_help()
