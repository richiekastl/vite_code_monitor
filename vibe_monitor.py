"""
Vibe Coding Monitor

A file system monitor that plays notification sounds when file activity stops.
Perfect for knowing when your builds, tests, or long-running tasks are complete.
"""

import os
import time
import sys
import json
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygame.mixer

# Initialize pygame mixer
pygame.mixer.init()

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to configuration file
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# Default configuration values
DEFAULT_CONFIG = {
    "excluded_files": [
        "debug.log",
        ".DS_Store",
        "Thumbs.db",
        "*.tmp",
        "*.temp",
        "*.swp",
        "*.lock"
    ],
    "excluded_folders": [
        "node_modules",
        ".git",
        "__pycache__",
        "logs",
        "tmp",
        "temp",
        "cache",
        "dist",
        "build"
    ],
    "sound_files": {
        "jobs-done": "sounds/jobs-done.mp3",
        "dolphin": "sounds/dolphin.mp3",
        "wow": "sounds/wow.mp3"
    },
    "settings": {
        "default_sound": "jobs-done",
        "default_delay": 60,
        "default_volume": 0.5
    }
}

def load_config():
    """Load configuration from JSON file or use defaults if file not found."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print(f"Configuration loaded from {CONFIG_FILE}")
                return config
        else:
            print(f"Configuration file not found at {CONFIG_FILE}, using defaults")
            # Create default config file for user
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
                print(f"Created default configuration file at {CONFIG_FILE}")
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG

# Load configuration
CONFIG = load_config()

# Get configured values with fallbacks
DEFAULT_EXCLUDED_FILES = CONFIG.get("excluded_files", DEFAULT_CONFIG["excluded_files"])
DEFAULT_EXCLUDED_FOLDERS = CONFIG.get("excluded_folders", DEFAULT_CONFIG["excluded_folders"])
DEFAULT_DELAY = CONFIG.get("settings", {}).get("default_delay", 60)
DEFAULT_VOLUME = CONFIG.get("settings", {}).get("default_volume", 0.5)

# Build sound files dictionary with absolute paths
SOUND_FILES = {}
for sound_name, sound_path in CONFIG.get("sound_files", {}).items():
    # If path is relative, make it absolute based on script directory
    if not os.path.isabs(sound_path):
        sound_path = os.path.join(SCRIPT_DIR, sound_path)
    SOUND_FILES[sound_name] = sound_path

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, sound_key, excluded_files=None, excluded_folders=None, delay=DEFAULT_DELAY):
        self.last_change = time.time()
        self.has_alerted = False  # Flag to ensure single alert
        self.sound_key = sound_key  # Store the sound key
        self.excluded_files = excluded_files or DEFAULT_EXCLUDED_FILES
        self.excluded_folders = excluded_folders or DEFAULT_EXCLUDED_FOLDERS
        self.delay = delay

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)

            # Normalize paths for consistent comparison
            file_dir_normalized = os.path.normpath(file_dir).lower()
            for excluded_folder in self.excluded_folders:
                excluded_folder_normalized = os.path.normpath(excluded_folder).lower()
                if file_dir_normalized.startswith(excluded_folder_normalized) or excluded_folder_normalized in file_dir_normalized:
                    return

            # Check if file should be excluded
            for excluded_pattern in self.excluded_files:
                # Simple wildcard handling
                if excluded_pattern.startswith("*") and file_name.endswith(excluded_pattern[1:]):
                    return
                elif excluded_pattern == file_name:
                    return

            print(f"Change detected: {file_path}")
            self.last_change = time.time()
            self.has_alerted = False

    def check_completion(self):
        current_time = time.time()
        time_since_last_change = current_time - self.last_change
        print(f"Time since last change: {time_since_last_change:.2f} seconds")
        if not self.has_alerted and time_since_last_change >= self.delay:
            print("Activity stopped! Your task is likely complete.")
            play_system_sound(self.sound_key)  # Pass the sound key here
            self.has_alerted = True

def play_system_sound(sound_key):
    """Play the specified sound file at configured volume."""
    sound_file = SOUND_FILES.get(sound_key, SOUND_FILES.get(CONFIG.get("settings", {}).get("default_sound", "jobs-done")))
    print(f"Attempting to play sound file: {sound_file}")
    if not os.path.exists(sound_file):
        print(f"Error: Sound file not found at {sound_file}")
        return
    try:
        print("Playing sound notification...")
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(DEFAULT_VOLUME)  # Set volume from config
        sound.play()
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        print("Sound playback completed.")
    except Exception as e:
        print(f"Error playing sound: {e}")

def main(watch_path, sound_key, delay=None, exclude_file=None, exclude_dir=None):
    if not os.path.exists(watch_path):
        print(f"Error: Directory {watch_path} does not exist.")
        sys.exit(1)

    # Use configured delay if not specified in args
    actual_delay = delay if delay is not None else DEFAULT_DELAY

    # Load custom exclude lists if provided via command line
    excluded_files = DEFAULT_EXCLUDED_FILES
    if exclude_file:
        with open(exclude_file, 'r') as f:
            excluded_files = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    excluded_folders = DEFAULT_EXCLUDED_FOLDERS
    if exclude_dir:
        with open(exclude_dir, 'r') as f:
            excluded_folders = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    event_handler = FileChangeHandler(
        sound_key, 
        excluded_files=excluded_files, 
        excluded_folders=excluded_folders,
        delay=actual_delay
    )
    
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()

    print(f"Monitoring {watch_path} for changes...")
    print(f"Notification sound: {sound_key}")
    print(f"Activity timeout: {actual_delay} seconds")
    print(f"Notification volume: {DEFAULT_VOLUME * 100:.0f}%")
    print("Press Ctrl+C to stop monitoring.")
    
    try:
        while True:
            time.sleep(1)
            event_handler.check_completion()
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped monitoring.")
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Vibe Coding Monitor: Get notified when file changes stop in a directory."
    )
    parser.add_argument(
        "--watch_path", 
        type=str, 
        required=True, 
        help="Path to the folder to monitor (e.g., ./my-project)"
    )
    parser.add_argument(
        "--sound", 
        type=str, 
        default=CONFIG.get("settings", {}).get("default_sound", "jobs-done"), 
        choices=list(SOUND_FILES.keys()),
        help=f"Sound to play when done (default: {CONFIG.get('settings', {}).get('default_sound', 'jobs-done')})"
    )
    parser.add_argument(
        "--delay", 
        type=int, 
        default=None,
        help=f"Time in seconds to wait after last change before playing sound (default: {DEFAULT_DELAY})"
    )
    parser.add_argument(
        "--exclude-file", 
        type=str, 
        help="Path to file containing list of files to exclude (one per line)"
    )
    parser.add_argument(
        "--exclude-dir", 
        type=str, 
        help="Path to file containing list of directories to exclude (one per line)"
    )
    
    args = parser.parse_args()
    print(f"Starting Vibe Coding Monitor")
    main(
        args.watch_path, 
        args.sound, 
        delay=args.delay,
        exclude_file=args.exclude_file,
        exclude_dir=args.exclude_dir
    )