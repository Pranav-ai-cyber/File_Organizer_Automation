#!/usr/bin/env python3
"""
File Organizer - Production-Grade Automation Script
Author: File Organization System
Version: 1.0.0
Description: Automatically organize files by type with advanced features
"""

import os
import sys
import json
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from logging.handlers import RotatingFileHandler
from collections import defaultdict
import time

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Install 'rich' for better UI: pip install rich")

# ASCII Art Banner
BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██╗██╗     ███████╗     ██████╗ ██████╗  ██╗   ║
║   ██╔════╝██║██║     ██╔════╝    ██╔═══██╗██╔══██╗██╔╝   ║
║   █████╗  ██║██║     █████╗      ██║   ██║██████╔╝██║    ║
║   ██╔══╝  ██║██║     ██╔══╝      ██║   ██║██╔══██╗██║    ║
║   ██║     ██║███████╗███████╗    ╚██████╔╝██║  ██║╚██╗   ║
║   ╚═╝     ╚═╝╚══════╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝ ╚═╝   ║
║                                                           ║
║            Intelligent File Organization System           ║
║                      Version 1.0.0                        ║
╚═══════════════════════════════════════════════════════════╝
"""

# Default configuration
DEFAULT_CONFIG = {
    "categories": {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", 
                     ".xlsx", ".ppt", ".pptx", ".csv", ".md", ".tex"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", 
                  ".tiff", ".webp", ".heic", ".raw"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", 
                  ".m4v", ".mpg", ".mpeg"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", 
                 ".opus", ".aiff"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", 
                    ".iso", ".dmg"],
        "Code": [".py", ".js", ".java", ".cpp", ".c", ".h", ".cs", ".php", 
                ".rb", ".go", ".rs", ".swift", ".kt", ".html", ".css", ".sql"],
        "Executables": [".exe", ".msi", ".app", ".deb", ".rpm", ".apk"],
        "Others": []
    },
    "ignore_files": [".ds_store", "thumbs.db", "desktop.ini"],
    "ignore_folders": ["organized_files", "node_modules", ".git", "__pycache__"],
    "duplicate_strategy": "rename",  # Options: rename, skip, overwrite
    "log_file": "file_organizer.log",
    "log_level": "INFO",
    "max_log_size": 5242880,  # 5MB
    "backup_count": 3
}

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'

class FileOrganizerError(Exception):
    """Base exception for File Organizer"""
    pass

class ConfigError(FileOrganizerError):
    """Configuration related errors"""
    pass

class OrganizationError(FileOrganizerError):
    """File organization related errors"""
    pass

class FileOrganizer:
    """
    Production-grade file organizer with advanced features.
    
    Attributes:
        source_path (Path): Directory to organize
        config (Dict): Configuration dictionary
        logger (logging.Logger): Logger instance
        console (Console): Rich console for output
        dry_run (bool): Preview mode flag
        stats (Dict): Operation statistics
    """
    
    def __init__(self, source_path: str, config_path: Optional[str] = None, 
                 dry_run: bool = False, verbose: bool = False, quiet: bool = False):
        """
        Initialize the File Organizer.
        
        Args:
            source_path: Path to directory to organize
            config_path: Path to custom config file
            dry_run: If True, only preview changes
            verbose: Enable detailed output
            quiet: Minimize output
            
        Raises:
            FileNotFoundError: If source path doesn't exist
            ConfigError: If config file is invalid
        """
        self.source_path = Path(source_path).resolve()
        self.dry_run = dry_run
        self.verbose = verbose
        self.quiet = quiet
        self.console = Console() if RICH_AVAILABLE else None
        self.history_file = self.source_path / ".file_organizer_history.json"
        
        # Validate source path
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {self.source_path}")
        if not self.source_path.is_dir():
            raise NotADirectoryError(f"Source path is not a directory: {self.source_path}")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize statistics
        self.stats = {
            "total_files": 0,
            "organized": 0,
            "skipped": 0,
            "errors": 0,
            "categories": defaultdict(int),
            "start_time": None,
            "end_time": None
        }
        
        # Current operation history
        self.current_operation: List[Tuple[Path, Path]] = []
        
        self.logger.info(f"FileOrganizer initialized for: {self.source_path}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigError: If config file is invalid
        """
        if config_path:
            config_file = Path(config_path)
            if not config_file.exists():
                raise ConfigError(f"Config file not found: {config_path}")
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    # Merge with defaults
                    config = DEFAULT_CONFIG.copy()
                    config.update(custom_config)
                    self._validate_config(config)
                    return config
            except json.JSONDecodeError as e:
                raise ConfigError(f"Invalid JSON in config file: {e}")
        
        return DEFAULT_CONFIG.copy()
    
    def _validate_config(self, config: Dict) -> None:
        """
        Validate configuration structure.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ConfigError: If configuration is invalid
        """
        required_keys = ["categories", "duplicate_strategy"]
        for key in required_keys:
            if key not in config:
                raise ConfigError(f"Missing required config key: {key}")
        
        if not isinstance(config["categories"], dict):
            raise ConfigError("'categories' must be a dictionary")
        
        valid_strategies = ["rename", "skip", "overwrite"]
        if config["duplicate_strategy"] not in valid_strategies:
            raise ConfigError(f"Invalid duplicate_strategy. Must be one of: {valid_strategies}")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup rotating file logger.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("FileOrganizer")
        logger.setLevel(getattr(logging, self.config.get("log_level", "INFO")))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # File handler with rotation
        log_file = self.source_path / self.config.get("log_file", "file_organizer.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.get("max_log_size", 5242880),
            backupCount=self.config.get("backup_count", 3),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler for errors
        if not self.quiet:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _get_category(self, file_path: Path) -> str:
        """
        Determine file category based on extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Category name
        """
        extension = file_path.suffix.lower()
        
        for category, extensions in self.config["categories"].items():
            if extension in extensions:
                return category
        
        return "Others"
    
    def _should_ignore(self, file_path: Path) -> bool:
        """
        Check if file should be ignored.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be ignored
        """
        # Check ignore list
        if file_path.name.lower() in self.config.get("ignore_files", []):
            return True
        
        # Check if in ignore folder
        for parent in file_path.parents:
            if parent.name in self.config.get("ignore_folders", []):
                return True
        
        # Ignore hidden files (except on Windows where many system files are hidden)
        if file_path.name.startswith('.') and sys.platform != 'win32':
            return True
        
        # Ignore symbolic links
        if file_path.is_symlink():
            return True
        
        return False
    
    def _generate_unique_name(self, target_path: Path) -> Path:
        """
        Generate unique filename if duplicate exists.
        
        Args:
            target_path: Intended destination path
            
        Returns:
            Unique file path
        """
        if not target_path.exists():
            return target_path
        
        strategy = self.config.get("duplicate_strategy", "rename")
        
        if strategy == "skip":
            return None
        elif strategy == "overwrite":
            return target_path
        
        # Rename strategy
        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        counter = 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try with timestamp first
        new_path = parent / f"{stem}_{timestamp}{suffix}"
        if not new_path.exists():
            return new_path
        
        # If still exists, add counter
        while True:
            new_path = parent / f"{stem}_{timestamp}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
            if counter > 1000:  # Safety limit
                raise OrganizationError(f"Could not generate unique name for {target_path}")
    
    def _move_file(self, source: Path, destination: Path) -> bool:
        """
        Move file with error handling.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check disk space
            if not self.dry_run:
                stat = os.statvfs(destination.parent) if hasattr(os, 'statvfs') else None
                if stat:
                    available_space = stat.f_bavail * stat.f_frsize
                    file_size = source.stat().st_size
                    if available_space < file_size * 1.1:  # 10% buffer
                        self.logger.error(f"Insufficient disk space for {source.name}")
                        return False
            
            # Perform move
            if not self.dry_run:
                shutil.move(str(source), str(destination))
                self.current_operation.append((source, destination))
            
            self.logger.info(f"Moved: {source} -> {destination}")
            return True
            
        except PermissionError:
            self.logger.error(f"Permission denied: {source}")
            return False
        except OSError as e:
            self.logger.error(f"OS error moving {source}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error moving {source}: {e}")
            return False
    
    def _scan_files(self, recursive: bool = False) -> List[Path]:
        """
        Scan directory for files to organize.
        
        Args:
            recursive: Include subdirectories
            
        Returns:
            List of file paths
        """
        files = []
        
        try:
            if recursive:
                for root, dirs, filenames in os.walk(self.source_path):
                    # Remove ignored directories from traversal
                    dirs[:] = [d for d in dirs if d not in self.config.get("ignore_folders", [])]
                    
                    for filename in filenames:
                        file_path = Path(root) / filename
                        if not self._should_ignore(file_path):
                            files.append(file_path)
            else:
                for item in self.source_path.iterdir():
                    if item.is_file() and not self._should_ignore(item):
                        files.append(item)
        
        except PermissionError as e:
            self.logger.error(f"Permission denied scanning directory: {e}")
        
        return files
    
    def organize(self, recursive: bool = False) -> Dict:
        """
        Main organization method.
        
        Args:
            recursive: Include subdirectories
            
        Returns:
            Statistics dictionary
        """
        self.stats["start_time"] = datetime.now()
        
        # Print banner
        if not self.quiet:
            if self.console:
                self.console.print(BANNER, style="cyan bold")
                if self.dry_run:
                    self.console.print("[yellow]🔍 DRY RUN MODE - No files will be moved[/yellow]\n")
            else:
                print(Colors.CYAN + BANNER + Colors.RESET)
                if self.dry_run:
                    print(Colors.YELLOW + "🔍 DRY RUN MODE - No files will be moved" + Colors.RESET)
        
        # Scan files
        files = self._scan_files(recursive)
        self.stats["total_files"] = len(files)
        
        if not files:
            self._print_message("No files to organize.", "yellow")
            return self.stats
        
        self._print_message(f"Found {len(files)} file(s) to organize.", "blue")
        
        # Organize files with progress bar
        if self.console and not self.quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                task = progress.add_task("[cyan]Organizing files...", total=len(files))
                
                for file_path in files:
                    self._organize_single_file(file_path)
                    progress.update(task, advance=1)
        else:
            # Simple progress without rich
            for i, file_path in enumerate(files, 1):
                self._organize_single_file(file_path)
                if not self.quiet and i % 10 == 0:
                    print(f"Progress: {i}/{len(files)}")
        
        self.stats["end_time"] = datetime.now()
        
        # Save operation history
        if not self.dry_run and self.current_operation:
            self._save_history()
        
        # Print summary
        self._print_summary()
        
        return self.stats
    
    def _organize_single_file(self, file_path: Path) -> None:
        """
        Organize a single file.
        
        Args:
            file_path: Path to file
        """
        try:
            # Determine category
            category = self._get_category(file_path)
            self.stats["categories"][category] += 1
            
            # Create category directory
            category_dir = self.source_path / category
            if not self.dry_run:
                category_dir.mkdir(exist_ok=True)
            
            # Generate destination path
            destination = category_dir / file_path.name
            
            # Handle duplicates
            unique_destination = self._generate_unique_name(destination)
            if unique_destination is None:
                self.stats["skipped"] += 1
                self.logger.info(f"Skipped duplicate: {file_path.name}")
                return
            
            # Move file
            if self._move_file(file_path, unique_destination):
                self.stats["organized"] += 1
                if self.verbose and not self.quiet:
                    self._print_message(f"✓ {file_path.name} -> {category}/", "green")
            else:
                self.stats["errors"] += 1
        
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Error organizing {file_path}: {e}")
    
    def _save_history(self) -> None:
        """Save operation history for undo functionality."""
        try:
            history = {
                "timestamp": datetime.now().isoformat(),
                "operations": [
                    {"source": str(src), "destination": str(dst)}
                    for src, dst in self.current_operation
                ]
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
            
            self.logger.info(f"Saved operation history: {len(self.current_operation)} operations")
        
        except Exception as e:
            self.logger.error(f"Failed to save history: {e}")
    
    def undo(self) -> bool:
        """
        Undo last organization operation.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.history_file.exists():
            self._print_message("No history found. Nothing to undo.", "yellow")
            return False
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            operations = history.get("operations", [])
            if not operations:
                self._print_message("No operations to undo.", "yellow")
                return False
            
            self._print_message(f"Undoing {len(operations)} operation(s)...", "blue")
            
            success_count = 0
            for op in reversed(operations):
                src = Path(op["source"])
                dst = Path(op["destination"])
                
                if dst.exists():
                    try:
                        shutil.move(str(dst), str(src))
                        success_count += 1
                        self.logger.info(f"Undone: {dst} -> {src}")
                    except Exception as e:
                        self.logger.error(f"Failed to undo {dst}: {e}")
            
            # Remove empty category directories
            for category in self.config["categories"].keys():
                category_dir = self.source_path / category
                if category_dir.exists() and not any(category_dir.iterdir()):
                    category_dir.rmdir()
            
            # Delete history file
            self.history_file.unlink()
            
            self._print_message(f"✓ Successfully undone {success_count}/{len(operations)} operation(s).", "green")
            return True
        
        except Exception as e:
            self.logger.error(f"Error during undo: {e}")
            self._print_message(f"Error during undo: {e}", "red")
            return False
    
    def _print_summary(self) -> None:
        """Print operation summary."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        if self.console and not self.quiet:
            # Rich formatted summary
            table = Table(title="📊 Organization Summary", show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Files", str(self.stats["total_files"]))
            table.add_row("Organized", str(self.stats["organized"]))
            table.add_row("Skipped", str(self.stats["skipped"]))
            table.add_row("Errors", str(self.stats["errors"]))
            table.add_row("Time Taken", f"{duration:.2f}s")
            
            self.console.print("\n")
            self.console.print(table)
            
            # Category breakdown
            if self.stats["categories"]:
                cat_table = Table(title="📁 Files by Category", show_header=True, header_style="bold blue")
                cat_table.add_column("Category", style="yellow")
                cat_table.add_column("Count", style="green")
                
                for category, count in sorted(self.stats["categories"].items(), key=lambda x: x[1], reverse=True):
                    cat_table.add_row(category, str(count))
                
                self.console.print(cat_table)
        else:
            # Plain text summary
            print("\n" + "="*50)
            print("📊 ORGANIZATION SUMMARY")
            print("="*50)
            print(f"Total Files:    {self.stats['total_files']}")
            print(f"Organized:      {self.stats['organized']}")
            print(f"Skipped:        {self.stats['skipped']}")
            print(f"Errors:         {self.stats['errors']}")
            print(f"Time Taken:     {duration:.2f}s")
            print("="*50)
            
            if self.stats["categories"]:
                print("\n📁 FILES BY CATEGORY:")
                for category, count in sorted(self.stats["categories"].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {category:15s} : {count}")
                print("="*50)
    
    def _print_message(self, message: str, color: str = "white") -> None:
        """
        Print colored message.
        
        Args:
            message: Message to print
            color: Color name
        """
        if self.quiet:
            return
        
        if self.console:
            self.console.print(f"[{color}]{message}[/{color}]")
        else:
            color_code = getattr(Colors, color.upper(), Colors.WHITE)
            print(f"{color_code}{message}{Colors.RESET}")


def create_default_config(path: str = "config.json") -> None:
    """
    Create default configuration file.
    
    Args:
        path: Path for config file
    """
    config_path = Path(path)
    if config_path.exists():
        print(f"Config file already exists: {path}")
        return
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    
    print(f"✓ Created default config file: {path}")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Intelligent File Organization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -p /path/to/directory
  %(prog)s -p ~/Downloads --dry-run
  %(prog)s -p ~/Documents -r -v
  %(prog)s --undo -p /path/to/directory
  %(prog)s --create-config

For more information, visit: https://github.com/AryanPatel03/File_Organizer-Automation_Script
        """
    )
    
    parser.add_argument(
        '-p', '--path',
        type=str,
        help='Target directory path to organize'
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to custom configuration file'
    )
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Preview changes without moving files'
    )
    parser.add_argument(
        '-u', '--undo',
        action='store_true',
        help='Undo last organization operation'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Include subdirectories'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable detailed output'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output'
    )
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default config.json file'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='File Organizer v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Handle config creation
    if args.create_config:
        create_default_config()
        return 0
    
    # Require path for other operations
    if not args.path:
        parser.print_help()
        print("\n❌ Error: --path is required")
        return 1
    
    try:
        organizer = FileOrganizer(
            source_path=args.path,
            config_path=args.config,
            dry_run=args.dry_run,
            verbose=args.verbose,
            quiet=args.quiet
        )
        
        if args.undo:
            success = organizer.undo()
            return 0 if success else 1
        else:
            stats = organizer.organize(recursive=args.recursive)
            return 0 if stats["errors"] == 0 else 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 130
    except FileOrganizerError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())