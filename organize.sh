#!/bin/bash

##############################################################################
# File Organizer - Quick Launch Script (Linux/Mac)
# Usage: ./organize.sh [path] [options]
##############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Print banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║          File Organizer - Quick Launch Script            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if file_organizer.py exists
if [ ! -f "$SCRIPT_DIR/file_organizer.py" ]; then
    echo -e "${RED}❌ Error: file_organizer.py not found${NC}"
    echo "Please run this script from the project directory"
    exit 1
fi

# Function to show help
show_help() {
    echo "Usage: ./organize.sh [OPTIONS]"
    echo ""
    echo "Common commands:"
    echo "  ./organize.sh                          - Interactive mode"
    echo "  ./organize.sh ~/Downloads              - Organize Downloads"
    echo "  ./organize.sh ~/Downloads --dry-run    - Preview changes"
    echo "  ./organize.sh ~/Downloads -v           - Verbose mode"
    echo "  ./organize.sh --help                   - Show this help"
    echo ""
}

# Interactive mode if no arguments
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}🔧 Interactive Mode${NC}"
    echo ""
    
    # Ask for path
    echo -e "${BLUE}Enter the directory path to organize:${NC}"
    read -p "Path (e.g., ~/Downloads): " TARGET_PATH
    
    if [ -z "$TARGET_PATH" ]; then
        echo -e "${RED}❌ No path provided. Exiting.${NC}"
        exit 1
    fi
    
    # Expand tilde
    TARGET_PATH="${TARGET_PATH/#\~/$HOME}"
    
    # Check if path exists
    if [ ! -d "$TARGET_PATH" ]; then
        echo -e "${RED}❌ Error: Directory does not exist: $TARGET_PATH${NC}"
        exit 1
    fi
    
    # Ask for dry run
    echo ""
    echo -e "${BLUE}Preview changes first (dry run)? [Y/n]:${NC}"
    read -p "> " DRY_RUN
    
    if [ "$DRY_RUN" != "n" ] && [ "$DRY_RUN" != "N" ]; then
        echo ""
        echo -e "${YELLOW}🔍 Running in DRY RUN mode...${NC}"
        python3 "$SCRIPT_DIR/file_organizer.py" -p "$TARGET_PATH" --dry-run
        
        echo ""
        echo -e "${BLUE}Proceed with actual organization? [y/N]:${NC}"
        read -p "> " PROCEED
        
        if [ "$PROCEED" = "y" ] || [ "$PROCEED" = "Y" ]; then
            echo ""
            echo -e "${GREEN}✓ Organizing files...${NC}"
            python3 "$SCRIPT_DIR/file_organizer.py" -p "$TARGET_PATH"
        else
            echo -e "${YELLOW}⚠️  Organization cancelled${NC}"
            exit 0
        fi
    else
        echo ""
        echo -e "${GREEN}✓ Organizing files...${NC}"
        python3 "$SCRIPT_DIR/file_organizer.py" -p "$TARGET_PATH"
    fi
    
else
    # Command line mode
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_help
        exit 0
    fi
    
    # Pass all arguments to Python script
    python3 "$SCRIPT_DIR/file_organizer.py" "$@"
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Operation completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Operation failed. Check the log file for details.${NC}"
    exit 1
fi