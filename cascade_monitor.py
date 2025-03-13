import os
import time
import sys
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from playsound import playsound

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Timer delay in seconds (60 seconds after last change)
DELAY = 60

# Files to ignore (common across projects)
EXCLUDED_FILES = [
    "debug.log",
    "wc-image-regeneration-2025-03-11-2d23918eaa6bf399fc1a4734d3e73c71.log"
]

# Folders to ignore (relative to watch_path or absolute; case-insensitive)
EXCLUDED_FOLDERS = [
    "wp-content/uploads",
    "wp-content/debug-logs",
    "wp-content/uploads/betheme/css",
    "wp-content/plugins/admin-columns-pro",
    "wp-content/plugins/autologin-links",
    "wp-content/plugins/svg-support",
    "wp-content/plugins/aryo-activity-log"
]

# Dictionary of available sound files
SOUND_FILES = {
    "jobs-done": os.path.join(SCRIPT_DIR, "sounds", "jobs-done.mp3"),
    "dolphin": os.path.join(SCRIPT_DIR, "sounds", "dolphin.mp3"),
    "wow": os.path.join(SCRIPT_DIR, "sounds", "wow.mp3")
}

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, sound_key):
        self.last_change = time.time()
        self.has_alerted = False  # Flag to ensure single alert
        self.sound_key = sound_key  # Store the sound key

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)

            # Normalize paths for consistent comparison
            file_dir_normalized = os.path.normpath(file_dir).lower()
            for excluded_folder in EXCLUDED_FOLDERS:
                excluded_folder_normalized = os.path.normpath(excluded_folder).lower()
                if file_dir_normalized.startswith(excluded_folder_normalized) or excluded_folder_normalized in file_dir_normalized:
                    return

            if any(excluded in file_name for excluded in EXCLUDED_FILES):
                return

            print(f"Change detected: {file_path}")
            self.last_change = time.time()
            self.has_alerted = False

    def check_completion(self):
        current_time = time.time()
        time_since_last_change = current_time - self.last_change
        print(f"Time since last change: {time_since_last_change:.2f} seconds")
        if not self.has_alerted and time_since_last_change >= DELAY:
            print("Cascade likely finished!")
            play_system_sound(self.sound_key)  # Pass the sound key here
            self.has_alerted = True

def play_system_sound(sound_key):
    """Play the specified sound file on Windows."""
    sound_file = SOUND_FILES.get(sound_key, SOUND_FILES["jobs-done"])  # Default to jobs-done if invalid
    print(f"Attempting to play sound file: {sound_file}")
    if not os.path.exists(sound_file):
        print(f"Error: Sound file not found at {sound_file}")
        return
    try:
        print("Playing sound using playsound...")
        playsound(sound_file)
        print("Sound playback completed.")
    except Exception as e:
        print(f"Error playing sound: {e}")

def main(watch_path, sound_key):
    if not os.path.exists(watch_path):
        print(f"Error: Directory {watch_path} does not exist.")
        sys.exit(1)

    event_handler = FileChangeHandler(sound_key)  # Pass sound_key to the handler
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()

    print(f"Monitoring {watch_path} for changes with sound: {sound_key}...")
    try:
        while True:
            time.sleep(1)
            event_handler.check_completion()
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped monitoring.")
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a folder for file changes and alert once when activity stops.")
    parser.add_argument("--watch_path", type=str, required=True, help="Path to the folder to monitor (e.g., ./my-project)")
    parser.add_argument("--sound", type=str, default="jobs-done", choices=["jobs-done", "dolphin", "wow"],
                        help="Sound to play when done (default: jobs-done)")
    args = parser.parse_args()
    print(f"Selected sound: {args.sound}")
    main(args.watch_path, args.sound)