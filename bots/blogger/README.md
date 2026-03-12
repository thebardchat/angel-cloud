# Black Crab Park Blog Bot

Automated posting bot for the Black Crab Park blog on Blogger.

## Features

- **Automated Posting**: Posts every 3 days automatically
- **AI Content Generation**: Uses local Ollama LLM for content (falls back to templates)
- **Multiple Modes**: Daemon, cron, or manual posting
- **Draft Support**: Create drafts for review before publishing
- **Post Queue**: Queue posts for later publishing

## Quick Start

```bash
# 1. Install dependencies
pip install google-api-python-client google-auth-oauthlib requests

# 2. Run setup wizard
python bot.py --setup

# 3. Check status
python bot.py --status

# 4. Interactive mode
python bot.py
```

## Setup

### 1. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing one
3. Enable the **Blogger API**
4. Go to **APIs & Services > Credentials**
5. Create **OAuth 2.0 Client ID** (Desktop app)
6. Download JSON and save as `credentials.json` in this folder

### 2. Get Your Blog ID

Your Blog ID is in the Blogger URL:
```
https://www.blogger.com/blog/posts/YOUR_BLOG_ID_HERE
```

Or go to Blogger Dashboard > Settings > scroll to Blog ID

### 3. Configure

Edit `config.py`:

```python
BLOG_CONFIG = {
    "blog_id": "YOUR_ACTUAL_BLOG_ID",
    "blog_url": "https://blackcrabpark.blogspot.com",
    "post_interval_days": 3,
    ...
}
```

### 4. First Run (OAuth)

```bash
python bot.py --status
```

This will open a browser for Google OAuth. Sign in and authorize.
Token is saved to `blogger_token.json` for future use.

## Usage

### Interactive Mode
```bash
python bot.py
```

### Check Status
```bash
python bot.py --status
```

### Post Now
```bash
# Create draft
python bot.py --post

# Publish immediately
python bot.py --post --publish

# With specific topic
python bot.py --post --topic "park cleanup day"
```

### Run Scheduler

**Option 1: Daemon Mode**
```bash
python bot.py --schedule
# or
python scheduler.py --daemon
```

**Option 2: Cron Job**
```bash
# Show cron entry
python scheduler.py --cron

# Add to crontab
crontab -e
# Paste the cron line
```

**Option 3: Systemd Service (Pi)**
```bash
# Generate service file
python scheduler.py --systemd > /tmp/blackcrab-blogger.service
sudo mv /tmp/blackcrab-blogger.service /etc/systemd/system/
sudo systemctl enable blackcrab-blogger
sudo systemctl start blackcrab-blogger
```

## AI Content Generation

The bot can use local Ollama for content generation:

```bash
# On your Pi 5, install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# The bot will auto-detect Ollama at localhost:11434
```

If Ollama is unavailable, the bot uses built-in templates.

## File Structure

```
bots/blogger/
├── bot.py              # Main controller
├── config.py           # Configuration
├── blogger_api.py      # Blogger API client
├── content_generator.py # AI/template content
├── scheduler.py        # Scheduling logic
├── credentials.json    # Google OAuth (you provide)
├── blogger_token.json  # OAuth token (auto-generated)
├── scheduler_state.json # Scheduler state
├── post_queue.json     # Queued posts
├── drafts/             # Draft previews
├── posted/             # Post logs
└── logs/               # Scheduler logs
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLOGGER_BLOG_ID` | - | Your Blogger blog ID |
| `GOOGLE_CREDENTIALS_PATH` | `credentials.json` | OAuth credentials |
| `BLOGGER_TOKEN_PATH` | `blogger_token.json` | OAuth token |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model to use |

## Testing

```bash
# Mock mode (no actual posting)
python bot.py --mock --post

# Check mock drafts in drafts/ folder
```

## Troubleshooting

**"Credentials file not found"**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in this folder

**"Blog ID not set"**
- Get Blog ID from Blogger dashboard URL
- Update `config.py` or set `BLOGGER_BLOG_ID` env var

**"Ollama not available"**
- Bot will use templates instead
- To enable AI: Install Ollama and run a model

**"Token expired"**
- Delete `blogger_token.json` and re-authenticate
