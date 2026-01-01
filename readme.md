# 📁 File Organizer - Intelligent Automation System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

**A production-grade Python automation script that intelligently organizes your files by type with advanced features like undo functionality, duplicate handling, and comprehensive logging.**

---

## Features

### Core Functionality
- **Smart File Classification** - Automatically categorizes files into Documents, Images, Videos, Audio, Archives, Code, and more
- **Duplicate Handling** - Three strategies: rename with timestamps, skip, or overwrite
- **Undo Functionality** - Reverse any organization operation with a single command
- **Dry Run Mode** - Preview changes before applying them
- **Real-time Progress** - Beautiful progress bars and status updates
- **Rich Terminal UI** - Colored output with tables and panels

### Advanced Features
- **Configurable Categories** - Customize file types via external JSON config
- **Recursive Organization** - Process subdirectories optionally
- **Comprehensive Logging** - Rotating logs with configurable levels
- **Error Recovery** - Handles permissions, disk space, and edge cases
- **Symbolic Link Support** - Safely handles symlinks
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **Detailed Statistics** - Summary reports with time taken and file counts

### Safety Features
- Never overwrites files (by default)
- Skips system files automatically
- Validates disk space before operations
- Creates backups of operation history
- Handles files currently in use

---

## Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Command Reference](#-command-reference)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download
```bash
# Clone the repository
git clone https://github.com/AryanPatel03/File_Organizer-Automation_Script.git
cd file-organizer

# Or download ZIP and extract
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or install manually
pip install rich colorama
```

### Step 3: Verify Installation
```bash
python file_organizer.py --version
```

---

## Quick Start

### Basic Usage
```bash
# Organize files in Downloads folder
python file_organizer.py -p ~/Downloads

# Preview changes without moving files (dry run)
python file_organizer.py -p ~/Downloads --dry-run

# Organize with verbose output
python file_organizer.py -p ~/Documents -v

# Undo last organization
python file_organizer.py -p ~/Downloads --undo
```

### First Time Setup
```bash
# Create default configuration file
python file_organizer.py --create-config

# Edit config.json to customize categories
# Then run organization
python file_organizer.py -p /path/to/folder -c config.json
```

---

## Usage Examples

### Example 1: Organize Downloads Folder
```bash
python file_organizer.py -p ~/Downloads
```
**Output:**
```
╔═══════════════════════════════════════════════════════════╗
║            Intelligent File Organization System           ║
╚═══════════════════════════════════════════════════════════╝

Found 127 file(s) to organize.
Organizing files... ████████████████████ 100%

Organization Summary
┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric      ┃ Value ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Files │ 127   │
│ Organized   │ 125   │
│ Skipped     │ 2     │
│ Errors      │ 0     │
│ Time Taken  │ 3.45s │
└─────────────┴───────┘
```

### Example 2: Dry Run Before Organizing
```bash
python file_organizer.py -p ~/Documents --dry-run -v
```
This previews all changes without actually moving files.

### Example 3: Organize Recursively
```bash
python file_organizer.py -p ~/Projects -r
```
Processes all subdirectories within the Projects folder.

### Example 4: Custom Configuration
```bash
python file_organizer.py -p ~/Desktop -c my_config.json
```
Uses custom file categories defined in `my_config.json`.

### Example 5: Undo Organization
```bash
python file_organizer.py -p ~/Downloads --undo
```
Reverses the last organization operation.

### Example 6: Quiet Mode for Scripts
```bash
python file_organizer.py -p ~/Files -q
```
Minimal output, useful for automation scripts.

---

## Configuration

### Configuration File Structure

The `config.json` file controls how files are categorized:

```json
{
  "categories": {
    "Documents": [".pdf", ".docx", ".txt"],
    "Images": [".jpg", ".png", ".gif"],
    "Videos": [".mp4", ".avi", ".mkv"]
  },
  "duplicate_strategy": "rename",
  "log_level": "INFO"
}
```

### Available Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `categories` | Object | File type mappings | See config.json |
| `ignore_files` | Array | Files to skip | `[".ds_store", "thumbs.db"]` |
| `ignore_folders` | Array | Folders to skip | `["node_modules", ".git"]` |
| `duplicate_strategy` | String | How to handle duplicates | `"rename"` |
| `log_file` | String | Log file name | `"file_organizer.log"` |
| `log_level` | String | Logging detail | `"INFO"` |
| `max_log_size` | Number | Max log size in bytes | `5242880` (5MB) |
| `backup_count` | Number | Number of log backups | `3` |

### Duplicate Strategies

1. **rename** (default) - Adds timestamp to duplicate filenames
   - `document.pdf` → `document_20241015_143022.pdf`

2. **skip** - Keeps original file, skips duplicate

3. **overwrite** - Replaces existing file (use with caution!)

### Adding Custom Categories

Edit `config.json` to add new categories:

```json
{
  "categories": {
    "3D Models": [".obj", ".fbx", ".stl", ".blend"],
    "Database": [".db", ".sqlite", ".mdb"],
    "Ebooks": [".epub", ".mobi", ".azw"]
  }
}
```

---

## Command Reference

### Basic Commands

| Command | Short | Description |
|---------|-------|-------------|
| `--path` | `-p` | Target directory to organize |
| `--config` | `-c` | Custom config file path |
| `--dry-run` | `-d` | Preview without moving files |
| `--undo` | `-u` | Reverse last operation |
| `--recursive` | `-r` | Include subdirectories |
| `--verbose` | `-v` | Detailed output |
| `--quiet` | `-q` | Minimal output |
| `--create-config` | - | Generate default config.json |
| `--version` | - | Show version information |
| `--help` | `-h` | Display help message |

### Command Combinations

```bash
# Dry run with verbose output
python file_organizer.py -p ~/Desktop -d -v

# Recursive organization with custom config
python file_organizer.py -p ~/Files -r -c my_config.json

# Quiet mode for cron jobs
python file_organizer.py -p ~/Downloads -q
```

---

## Project Structure

```
file-organizer/
│
├── file_organizer.py      # Main script
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── user_guide.md          # Detailed user guide
├── .gitignore            # Git ignore rules
│
├── examples/             # Example files and demos
│   ├── sample_files/     # Test files for demonstration
│   └── screenshots/      # UI screenshots
│
└── scripts/              # Helper scripts
    ├── organize.sh       # Linux/Mac quick launcher
    └── organize.bat      # Windows quick launcher
```

---

## Troubleshooting

### Common Issues

#### 1. Permission Denied Error
**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# On Linux/Mac, add execute permissions
chmod +x file_organizer.py

# Or run with sudo (use cautiously)
sudo python file_organizer.py -p /path/to/folder
```

#### 2. Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'rich'`

**Solution:**
```bash
pip install -r requirements.txt
```

#### 3. Files Not Moving
**Problem:** Files are scanned but not organized

**Solution:**
- Check if you're in dry-run mode (`--dry-run`)
- Verify file extensions are in config.json
- Check log file for errors: `file_organizer.log`

#### 4. Undo Not Working
**Problem:** Undo command doesn't reverse changes

**Solution:**
- History file might be deleted
- Check for `.file_organizer_history.json` in the directory
- Undo only works for the most recent operation

#### 5. Slow Performance
**Problem:** Script is slow with many files

**Solution:**
```bash
# Disable verbose mode
python file_organizer.py -p ~/folder -q

# Process smaller batches
# Organize subdirectories individually
```

### Getting Help

1. Check the log file: `file_organizer.log`
2. Run with verbose mode: `-v`
3. Review the [User Guide](user_guide.md)
4. Open an issue on GitHub

---

## Before & After Examples

### Before Organization
```
Downloads/
├── vacation.jpg
├── report.pdf
├── song.mp3
├── movie.mp4
├── script.py
├── photo.png
├── document.docx
└── archive.zip
```

### After Organization
```
Downloads/
├── Documents/
│   ├── report.pdf
│   └── document.docx
├── Images/
│   ├── vacation.jpg
│   └── photo.png
├── Audio/
│   └── song.mp3
├── Videos/
│   └── movie.mp4
├── Code/
│   └── script.py
└── Archives/
    └── archive.zip
```

---

## Use Cases

1. **Cleaning Downloads Folder** - Organize accumulated downloads
2. **Project Management** - Sort project files by type
3. **Digital Housekeeping** - Regular desktop cleanup
4. **Backup Preparation** - Organize before backing up
5. **Media Libraries** - Sort photo/video collections
6. **Code Repositories** - Organize mixed file projects

---

## Security & Privacy

- **No Internet Connection Required** - Works completely offline
- **No Data Collection** - No telemetry or analytics
- **Local Processing** - All operations stay on your machine
- **Open Source** - Inspect the code yourself
- **No Admin Rights Needed** - Works with user permissions

---

## Performance

- **Speed:** Processes 1000+ files in under 10 seconds
- **Memory:** Low memory footprint (<50MB)
- **Efficiency:** Batch operations with minimal I/O
- **Scalability:** Handles directories with 10,000+ files

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone repository
git clone https://github.com/AryanPatel03/File_Organizer-Automation_Script.git

# Install dev dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

---

## Acknowledgments

- Built with Python 3
- UI powered by [Rich](https://github.com/Textualize/rich)
- Inspired by the need for better file organization

---

## Contact

- **Author:** Aryan Virani
- **Email:** aryanvirani@zohomail.in
- **GitHub:** [@AryanPatel03](https://github.com/AryanPatel03)
- **Project Link:** [https://github.com/AryanPatel03/File_Organizer-Automation_Script.git](https://github.com/AryanPatel03/File_Organizer-Automation_Script.git)

---

## Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ and Python**
