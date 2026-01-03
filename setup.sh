#!/bin/bash
# LogiBot Setup Script
# Automated installation and configuration

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════"
echo "          LogiBot / Angel Cloud Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${RED}✗ Python 3.8+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo -e "${GREEN}✓ Logs directory created${NC}"
fi

# Check for credentials file
if [ ! -f "credentials.json" ]; then
    echo -e "${YELLOW}⚠ credentials.json not found${NC}"
    echo "Please create credentials.json from credentials.json.template"
    echo "See SYNC_README.md for instructions"
else
    echo -e "${GREEN}✓ credentials.json found${NC}"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Make Python scripts executable
echo "Making scripts executable..."
chmod +x google_sheets_sync.py
chmod +x life_command_center_sync.py
chmod +x logibot_core.py
chmod +x webhook_receiver.py
chmod +x health_monitor.py
chmod +x test_sync.py
echo -e "${GREEN}✓ Scripts are executable${NC}"

# Run health check (optional)
echo ""
read -p "Run health check? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running health check..."
    python3 health_monitor.py || echo -e "${YELLOW}⚠ Health check reported issues${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Add credentials.json (service account file)"
echo "3. Run: source venv/bin/activate"
echo "4. Test: python3 google_sheets_sync.py"
echo "5. Start: python3 logibot_core.py"
echo ""
echo "For more information, see SYNC_README.md"
echo ""
