# Multi-Computer Sync Guide

**Sync Angel Cloud / LogiBot between Work and Home computers**

---

## Quick Start

### Initial Setup (Do Once)

#### Computer A (Work)
```bash
cd /path/to/angel-cloud

# Mount 8TB drive
sudo ./mount_8tb.sh

# Verify setup
python3 sync_verify.py

# Push to GitHub
./sync.sh push
```

#### Computer B (Home)
```bash
# Clone repository
git clone https://github.com/thebardchat/angel-cloud.git
cd angel-cloud

# Checkout branch
git checkout claude/setup-user-profile-9LdRn

# Setup environment
./setup.sh

# Mount 8TB drive
sudo ./mount_8tb.sh

# Pull from GitHub
./sync.sh pull
```

---

## Daily Workflow

### Leaving Work (Computer A → GitHub)
```bash
./sync.sh push
```

### Arriving Home (GitHub → Computer B)
```bash
./sync.sh pull
```

### Leaving Home (Computer B → GitHub)
```bash
./sync.sh push
```

### Arriving Work (GitHub → Computer A)
```bash
./sync.sh pull
```

---

## Sync Commands

### Interactive Mode
```bash
./sync.sh
```

Shows menu with options:
1. **Push** - Send local changes to GitHub
2. **Pull** - Get latest from GitHub
3. **Full Sync** - Push then pull
4. **Status** - Check sync status
5. **Verify** - Run verification checks
6. **8TB Sync** - Sync drive data between computers

### Command Line Mode
```bash
# Push local changes
./sync.sh push

# Pull remote changes
./sync.sh pull

# Full sync (push then pull)
./sync.sh sync

# Check status
./sync.sh status

# Verify integrity
./sync.sh verify

# Get help
./sync.sh help
```

---

## 8TB Drive Sync

### One-Time Setup

#### Computer A (Primary)
```bash
# Mount drive
sudo ./mount_8tb.sh

# Verify structure
ls -la /mnt/8tb_drive/legacy_ai/
```

#### Computer B (Secondary)
```bash
# Mount drive
sudo ./mount_8tb.sh

# Initial sync from Computer A
./sync.sh 8tb-pull user@work-pc.local
```

### Ongoing Sync

#### Push from A to B
```bash
# On Computer A
./sync.sh 8tb-push user@home-pc.local
```

#### Pull from A to B
```bash
# On Computer B
./sync.sh 8tb-pull user@work-pc.local
```

**Note:** Requires SSH access between computers.

### SSH Setup (Optional but Recommended)
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy to remote computer
ssh-copy-id user@remote-hostname

# Test connection
ssh user@remote-hostname
```

---

## Configuration

### Computer Profiles

Edit `computer_profiles.yaml`:

```yaml
computers:
  computer_a:
    name: "Work Computer"
    hostname: "work-pc"
    role: "primary"

  computer_b:
    name: "Home Computer"
    hostname: "home-pc"
    role: "secondary"
```

### Sync Strategy

**GitHub as Central Hub:**
- Computer A → GitHub → Computer B
- Always sync through GitHub
- 8TB drive syncs directly between computers (optional)

**What Gets Synced:**
- ✅ Code changes
- ✅ Configuration files (.env, training_config.yaml)
- ✅ Documentation updates
- ✅ 8TB drive: datasets, models, memory (manual)

**What Doesn't Sync:**
- ❌ venv/ (recreate on each computer)
- ❌ logs/ (local only)
- ❌ credentials.json (manual setup on each computer)
- ❌ __pycache__/ (auto-generated)

---

## Verification

### Before Syncing
```bash
python3 sync_verify.py
```

**Checks:**
- Git status (clean working tree)
- Branch (on correct branch)
- Remote sync (up to date with GitHub)
- 8TB drive (mounted correctly)
- Dependencies (venv exists)
- Ollama (installed and running)

### After Syncing
```bash
./sync.sh verify
```

---

## Conflict Resolution

### Scenario 1: Uncommitted Changes
```bash
# Error: "Cannot pull: uncommitted changes"

# Option 1: Commit changes
git add -A
git commit -m "Work in progress"
./sync.sh push

# Option 2: Stash changes
git stash
./sync.sh pull
git stash pop
```

### Scenario 2: Diverged Branches
```bash
# Error: "Diverged from remote"

# Check what diverged
git status
git log --oneline @{u}..HEAD  # Local commits
git log --oneline HEAD..@{u}  # Remote commits

# Resolve (choose one)
git pull --rebase  # Rebase local on top of remote
git pull --no-rebase  # Merge remote into local
```

### Scenario 3: Merge Conflicts
```bash
# After pull with conflicts
git status  # See conflicted files

# Edit files to resolve conflicts
# Look for <<<<<<< HEAD markers

# Mark as resolved
git add <file>
git commit

# Push resolution
./sync.sh push
```

---

## Automation

### Auto-Sync on Startup (Linux/WSL)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
# Auto-pull on terminal open
if [ -d "$HOME/angel-cloud" ]; then
    cd $HOME/angel-cloud
    ./sync.sh pull --quiet 2>/dev/null || true
fi
```

### Auto-Sync on Shutdown (systemd)

Create `/etc/systemd/system/angel-cloud-sync.service`:
```ini
[Unit]
Description=Angel Cloud Auto-Sync
Before=shutdown.target

[Service]
Type=oneshot
User=your-username
ExecStart=/home/your-username/angel-cloud/sync.sh push
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable angel-cloud-sync.service
```

---

## Troubleshooting

### Issue: 8TB Drive Not Mounted
```bash
# Check if drive connected
lsblk

# Mount manually
sudo ./mount_8tb.sh

# Verify mount
df -h | grep 8tb
```

### Issue: Git Push/Pull Fails
```bash
# Check network
ping github.com

# Check credentials
git config --list | grep user

# Test connection
ssh -T git@github.com

# Force push (use cautiously)
git push -f origin claude/setup-user-profile-9LdRn
```

### Issue: Sync Verification Fails
```bash
# Run with verbose logging
python3 sync_verify.py 2>&1 | tee verify.log

# Check specific issue
cat verify.log | grep "✗"

# Fix and re-verify
python3 sync_verify.py
```

### Issue: SSH Connection Fails (8TB Sync)
```bash
# Test SSH
ssh user@remote-hostname

# Check SSH service
sudo systemctl status ssh

# Check firewall
sudo ufw status
sudo ufw allow ssh
```

---

## Best Practices

1. **Always verify before syncing**
   ```bash
   ./sync.sh verify
   ```

2. **Commit meaningful messages**
   ```bash
   git commit -m "Add driver optimization for Plant XYZ"
   ```

3. **Sync frequently**
   - End of work day
   - Before starting work
   - After major changes

4. **Keep branches in sync**
   - Always work on `claude/setup-user-profile-9LdRn`
   - Don't create local branches

5. **Backup before major syncs**
   ```bash
   # Backup 8TB drive
   rsync -av /mnt/8tb_drive/legacy_ai/ /backup/legacy_ai_$(date +%Y%m%d)/
   ```

6. **Test after pulling**
   ```bash
   ./sync.sh pull
   python3 health_monitor.py
   ```

---

## Sync Checklist

### Before Leaving Work
- [ ] Commit all changes
- [ ] Run verification: `./sync.sh verify`
- [ ] Push to GitHub: `./sync.sh push`
- [ ] Verify push succeeded
- [ ] (Optional) Sync 8TB drive to home

### Before Starting Work at Home
- [ ] Pull from GitHub: `./sync.sh pull`
- [ ] Run verification: `./sync.sh verify`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Test system: `python3 health_monitor.py`

### Before Leaving Home
- [ ] Commit all changes
- [ ] Push to GitHub: `./sync.sh push`
- [ ] Verify push succeeded

### Before Starting Work at Office
- [ ] Pull from GitHub: `./sync.sh pull`
- [ ] Run verification: `./sync.sh verify`
- [ ] Test system: `python3 health_monitor.py`

---

## Advanced: Direct Computer-to-Computer Sync

### Using Syncthing (Real-time Sync)

1. **Install Syncthing** (both computers)
   ```bash
   sudo apt install syncthing
   ```

2. **Configure**
   - Add both computers as devices
   - Share `/mnt/8tb_drive/legacy_ai` folder
   - Enable auto-sync

3. **Verify**
   ```bash
   syncthing -browser-only
   ```

### Using Tailscale (Secure Network)

1. **Install Tailscale** (both computers)
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   ```

2. **Connect**
   ```bash
   sudo tailscale up
   ```

3. **Sync over Tailscale Network**
   ```bash
   # Much faster than over internet
   ./sync.sh 8tb-pull username@computer-name.tailnet
   ```

---

## Storage Requirements

### Per Computer

**Required:**
- Code repository: ~50 MB
- Virtual environment: ~500 MB
- Logs: ~10 MB/day

**Optional (8TB Drive):**
- Datasets: 1-10 MB
- Models: 1-3 GB each
- Memory: 1 MB/day
- Cache: Variable

### GitHub Usage

- Repository size: ~50 MB
- LFS not required (models stored locally)
- Free tier sufficient

---

## Security Considerations

1. **Credentials**
   - Never commit `credentials.json`
   - Store securely on each computer
   - Use same credentials or computer-specific

2. **SSH Keys**
   - Use separate SSH keys per computer
   - Add both to GitHub account
   - Use passphrase protection

3. **8TB Drive**
   - Encrypt drive (optional but recommended)
   - Use LUKS on Linux
   - Backup encryption keys securely

4. **Network**
   - Use SSH for rsync (encrypted)
   - Consider VPN for remote sync
   - Use Tailscale for zero-trust network

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Maintainer:** Shane Brazelton

**Mission:** Seamless work between office and home with zero friction.
