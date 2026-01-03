#!/bin/bash
# Multi-Computer Sync Script for Angel Cloud / LogiBot
# Syncs code, configs, and 8TB drive data between Computer A and Computer B

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BRANCH="claude/setup-user-profile-9LdRn"
COMPUTER_NAME=$(hostname)
SYNC_LOG="logs/sync_$(date +%Y%m%d_%H%M%S).log"

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}          Angel Cloud Multi-Computer Sync${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Computer: $COMPUTER_NAME"
echo "Branch: $BRANCH"
echo "Time: $(date)"
echo ""

# Function to check if 8TB drive is mounted
check_8tb_drive() {
    if [ -d "/mnt/8tb_drive" ]; then
        echo -e "${GREEN}✓ 8TB drive mounted${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ 8TB drive not mounted${NC}"
        return 1
    fi
}

# Function to push to GitHub
push_to_github() {
    echo -e "\n${BLUE}[PUSH] Syncing local changes to GitHub${NC}"

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}⚠ Uncommitted changes detected${NC}"
        read -p "Commit changes now? (y/n) " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Enter commit message (or press Enter for auto-generated):"
            read commit_msg

            if [ -z "$commit_msg" ]; then
                commit_msg="Auto-sync from $COMPUTER_NAME on $(date +%Y-%m-%d)"
            fi

            git add -A
            git commit -m "$commit_msg"
        else
            echo -e "${RED}✗ Skipping commit${NC}"
            return 1
        fi
    fi

    # Push to GitHub with retry
    echo "Pushing to GitHub..."
    git push -u origin $BRANCH || \
        (sleep 2 && git push -u origin $BRANCH) || \
        (sleep 4 && git push -u origin $BRANCH) || \
        (sleep 8 && git push -u origin $BRANCH)

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Push successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Push failed${NC}"
        return 1
    fi
}

# Function to pull from GitHub
pull_from_github() {
    echo -e "\n${BLUE}[PULL] Syncing GitHub changes to local${NC}"

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${RED}✗ Cannot pull: uncommitted changes detected${NC}"
        echo "Please commit or stash your changes first"
        return 1
    fi

    # Fetch latest
    echo "Fetching from GitHub..."
    git fetch origin $BRANCH

    # Check if behind
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})

    if [ $LOCAL = $REMOTE ]; then
        echo -e "${GREEN}✓ Already up to date${NC}"
        return 0
    fi

    # Pull changes
    echo "Pulling changes..."
    git pull origin $BRANCH

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Pull successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Pull failed${NC}"
        return 1
    fi
}

# Function to sync 8TB drive data
sync_8tb_drive() {
    local direction=$1  # "push" or "pull"
    local remote_host=$2

    if ! check_8tb_drive; then
        echo -e "${YELLOW}⚠ Skipping 8TB drive sync (not mounted)${NC}"
        return 0
    fi

    echo -e "\n${BLUE}[8TB SYNC] Syncing drive data ($direction)${NC}"

    LOCAL_PATH="/mnt/8tb_drive/legacy_ai"

    if [ -z "$remote_host" ]; then
        echo -e "${YELLOW}⚠ No remote host specified, skipping drive sync${NC}"
        return 0
    fi

    if [ "$direction" = "push" ]; then
        echo "Pushing 8TB data to $remote_host..."
        rsync -avz --progress \
            --exclude='*.pyc' \
            --exclude='__pycache__' \
            --exclude='.git' \
            $LOCAL_PATH/ \
            $remote_host:$LOCAL_PATH/
    else
        echo "Pulling 8TB data from $remote_host..."
        rsync -avz --progress \
            --exclude='*.pyc' \
            --exclude='__pycache__' \
            --exclude='.git' \
            $remote_host:$LOCAL_PATH/ \
            $LOCAL_PATH/
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 8TB drive sync successful${NC}"
        return 0
    else
        echo -e "${RED}✗ 8TB drive sync failed${NC}"
        return 1
    fi
}

# Function to verify sync integrity
verify_sync() {
    echo -e "\n${BLUE}[VERIFY] Checking sync integrity${NC}"

    # Check git status
    if git diff-index --quiet HEAD --; then
        echo -e "${GREEN}✓ Working tree clean${NC}"
    else
        echo -e "${YELLOW}⚠ Uncommitted changes present${NC}"
        git status --short
    fi

    # Check branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" = "$BRANCH" ]; then
        echo -e "${GREEN}✓ On correct branch: $BRANCH${NC}"
    else
        echo -e "${RED}✗ Wrong branch: $current_branch (expected $BRANCH)${NC}"
    fi

    # Check remote sync
    git fetch origin $BRANCH --quiet
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})

    if [ $LOCAL = $REMOTE ]; then
        echo -e "${GREEN}✓ Synced with remote${NC}"
    else
        echo -e "${YELLOW}⚠ Out of sync with remote${NC}"
    fi

    # Check 8TB drive
    check_8tb_drive

    # Check Python dependencies
    if [ -f "venv/bin/activate" ]; then
        echo -e "${GREEN}✓ Virtual environment exists${NC}"
    else
        echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
    fi
}

# Function to show sync status
show_status() {
    echo -e "\n${BLUE}[STATUS] Repository Status${NC}"

    git fetch origin $BRANCH --quiet

    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    BASE=$(git merge-base @ @{u})

    if [ $LOCAL = $REMOTE ]; then
        echo -e "${GREEN}Status: Up to date with remote${NC}"
    elif [ $LOCAL = $BASE ]; then
        echo -e "${YELLOW}Status: Behind remote (need to pull)${NC}"
    elif [ $REMOTE = $BASE ]; then
        echo -e "${YELLOW}Status: Ahead of remote (need to push)${NC}"
    else
        echo -e "${RED}Status: Diverged from remote${NC}"
    fi

    echo ""
    echo "Last 3 commits:"
    git log --oneline -3

    echo ""
    if git diff-index --quiet HEAD --; then
        echo "Working tree: Clean"
    else
        echo "Working tree: Modified files"
        git status --short
    fi
}

# Main menu
main_menu() {
    while true; do
        echo ""
        echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
        echo "Select sync operation:"
        echo "  1) Push - Send local changes to GitHub"
        echo "  2) Pull - Get latest changes from GitHub"
        echo "  3) Full Sync - Push local → Pull remote"
        echo "  4) Status - Check sync status"
        echo "  5) Verify - Verify sync integrity"
        echo "  6) 8TB Sync - Sync drive data (requires remote host)"
        echo "  0) Exit"
        echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

        read -p "Choice: " choice

        case $choice in
            1)
                push_to_github
                ;;
            2)
                pull_from_github
                ;;
            3)
                echo -e "${BLUE}[FULL SYNC] Push then Pull${NC}"
                push_to_github && pull_from_github
                ;;
            4)
                show_status
                ;;
            5)
                verify_sync
                ;;
            6)
                read -p "Enter remote host (user@hostname): " remote_host
                read -p "Push or Pull? (push/pull): " direction
                sync_8tb_drive "$direction" "$remote_host"
                ;;
            0)
                echo ""
                echo -e "${GREEN}Sync complete. Goodbye!${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
    done
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments - show menu
    show_status
    main_menu
else
    # Command line mode
    case $1 in
        push)
            push_to_github
            ;;
        pull)
            pull_from_github
            ;;
        sync)
            push_to_github && pull_from_github
            ;;
        status)
            show_status
            ;;
        verify)
            verify_sync
            ;;
        8tb-push)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: Remote host required${NC}"
                echo "Usage: $0 8tb-push user@hostname"
                exit 1
            fi
            sync_8tb_drive "push" "$2"
            ;;
        8tb-pull)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: Remote host required${NC}"
                echo "Usage: $0 8tb-pull user@hostname"
                exit 1
            fi
            sync_8tb_drive "pull" "$2"
            ;;
        help|--help|-h)
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  push           - Push local changes to GitHub"
            echo "  pull           - Pull remote changes from GitHub"
            echo "  sync           - Full sync (push then pull)"
            echo "  status         - Show sync status"
            echo "  verify         - Verify sync integrity"
            echo "  8tb-push HOST  - Sync 8TB drive to remote"
            echo "  8tb-pull HOST  - Sync 8TB drive from remote"
            echo "  help           - Show this help"
            echo ""
            echo "No arguments runs interactive mode"
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
fi
