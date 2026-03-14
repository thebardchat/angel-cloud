#!/bin/bash
# 8TB Drive Mount Helper
# Automatically mounts the 8TB external drive for Legacy AI training

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

MOUNT_POINT="/mnt/8tb_drive"
DRIVE_LABEL="LEGACY_AI_8TB"  # Change to your drive label

echo "8TB Drive Mount Helper"
echo "======================"
echo ""

# Check if already mounted
if mountpoint -q $MOUNT_POINT; then
    echo -e "${GREEN}✓ 8TB drive already mounted at $MOUNT_POINT${NC}"
    df -h $MOUNT_POINT
    exit 0
fi

# Create mount point if doesn't exist
if [ ! -d "$MOUNT_POINT" ]; then
    echo "Creating mount point: $MOUNT_POINT"
    sudo mkdir -p $MOUNT_POINT
fi

# Auto-detect drive
echo "Searching for 8TB drive..."

# Method 1: By label
DEVICE=$(blkid -L $DRIVE_LABEL 2>/dev/null)

# Method 2: By size (looking for ~8TB drive)
if [ -z "$DEVICE" ]; then
    echo "Drive label not found, searching by size..."

    # List all block devices and find large ones
    while IFS= read -r line; do
        if echo "$line" | grep -qE "7\.3T|8T"; then
            DEVICE=$(echo "$line" | awk '{print $1}')
            break
        fi
    done < <(lsblk -ndo NAME,SIZE /dev/sd*)
fi

# Method 3: Manual selection
if [ -z "$DEVICE" ]; then
    echo -e "${YELLOW}Could not auto-detect drive${NC}"
    echo ""
    echo "Available drives:"
    lsblk -o NAME,SIZE,LABEL,MOUNTPOINT
    echo ""
    read -p "Enter device path (e.g., /dev/sdb1): " DEVICE
fi

if [ -z "$DEVICE" ]; then
    echo -e "${RED}✗ No device specified${NC}"
    exit 1
fi

# Add /dev/ if not present
if [[ ! "$DEVICE" =~ ^/dev/ ]]; then
    DEVICE="/dev/$DEVICE"
fi

echo "Device: $DEVICE"

# Detect filesystem type
FS_TYPE=$(blkid -o value -s TYPE $DEVICE)
echo "Filesystem: $FS_TYPE"

# Mount the drive
echo "Mounting $DEVICE to $MOUNT_POINT..."

if [ "$FS_TYPE" = "ntfs" ]; then
    # NTFS requires special handling
    sudo mount -t ntfs-3g $DEVICE $MOUNT_POINT
else
    sudo mount $DEVICE $MOUNT_POINT
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully mounted${NC}"

    # Set permissions
    sudo chmod 777 $MOUNT_POINT

    # Create Legacy AI directory structure
    mkdir -p $MOUNT_POINT/legacy_ai/{datasets,models,memory,cache}

    echo ""
    echo "Drive Info:"
    df -h $MOUNT_POINT

    echo ""
    echo "Directory Structure:"
    ls -la $MOUNT_POINT/legacy_ai/

    # Add to fstab for auto-mount (optional)
    echo ""
    read -p "Add to /etc/fstab for automatic mounting? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        UUID=$(blkid -s UUID -o value $DEVICE)

        FSTAB_ENTRY="UUID=$UUID $MOUNT_POINT $FS_TYPE defaults,nofail 0 2"

        # Check if already in fstab
        if grep -q "$UUID" /etc/fstab; then
            echo -e "${YELLOW}⚠ Entry already exists in /etc/fstab${NC}"
        else
            echo "$FSTAB_ENTRY" | sudo tee -a /etc/fstab
            echo -e "${GREEN}✓ Added to /etc/fstab${NC}"
        fi
    fi
else
    echo -e "${RED}✗ Mount failed${NC}"
    exit 1
fi
