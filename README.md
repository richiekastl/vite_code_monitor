# Vibe Coding Monitor

A simple, configurable file system monitor that plays notification sounds when file activity stops. Perfect for knowing when your builds, tests, or long-running tasks are complete without having to constantly check!

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- 📂 Monitor any directory for file changes
- 🔊 Get audio notifications when file activity stops
- ⏱️ Configurable delay between last activity and notification
- 🚫 Exclude specific files and directories from monitoring
- 🎵 Choose from different notification sounds
- 🔊 Customizable notification volume
- ⚙️ JSON-based configuration for easy customization

## Installation

```bash
# Clone the repository
git clone https://github.com/richiekastl/vibe-coding-monitor.git
cd vibe-coding-monitor

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python vibe_monitor.py --watch_path /path/to/your/project
```

### All Options

```bash
python vibe_monitor.py --watch_path /path/to/your/project --sound "wow" --delay 30 --exclude-file excludes.txt --exclude-dir exclude-dirs.txt
```

### Command-line Arguments

- `--watch_path`: The directory to monitor for changes (required)
- `--sound`: Sound to play when activity stops (default: from config.json)
  - Available sounds are defined in config.json
- `--delay`: Time in seconds to wait after last change before playing sound (default: from config.json)
- `--exclude-file`: Path to a file containing a list of files to exclude (one per line)
- `--exclude-dir`: Path to a file containing a list of directories to exclude (one per line)

## Configuration

The application uses a JSON configuration file (`config.json`) in the same directory as the script. This file is created automatically on first run with default values, and you can customize it to your needs.

### Configuration Structure

```json
{
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
```

### Configuration Options

- `excluded_files`: List of filenames or patterns to ignore (supports simple wildcards)
- `excluded_folders`: List of folder paths to ignore
- `sound_files`: Mapping of sound names to file paths (relative to script or absolute)
- `settings`:
  - `default_sound`: Default sound to play (key from `sound_files`)
  - `default_delay`: Default time in seconds to wait after last file change
  - `default_volume`: Volume level from 0.0 (silent) to 1.0 (maximum)

### Example Exclude Files (for command-line arguments)

Example content for `excludes.txt`:
```
.DS_Store
Thumbs.db
*.log
*.tmp
```

Example content for `exclude-dirs.txt`:
```
node_modules
.git
__pycache__
dist
```

## Use Cases

- 🛠️ **Building Projects**: Know when your project build completes without constantly checking
- 🧪 **Running Tests**: Get notified when your test suite finishes
- 📦 **File Operations**: Be alerted when large file operations like copying or compression finish
- 🔄 **Database Operations**: Get alerted when a database backup or restore completes
- 📝 **Document Processing**: Know when batch document generation or processing is done

## Customization

### Adding Your Own Sounds

There are two ways to add custom sounds:

1. **Using config.json (Recommended)**:
   - Add your sounds to the `sounds` directory
   - Edit the `sound_files` section in `config.json`:
   ```json
   "sound_files": {
     "jobs-done": "sounds/jobs-done.mp3",
     "dolphin": "sounds/dolphin.mp3",
     "wow": "sounds/wow.mp3",
     "your-sound": "sounds/your-sound.mp3"
   }
   ```

2. **Using an absolute path**:
   ```json
   "sound_files": {
     "custom-alarm": "C:/Path/To/Your/Sound/file.mp3"
   }
   ```

### Adjusting Volume

Edit the `default_volume` in the `settings` section of `config.json`:
```json
"settings": {
  "default_volume": 0.3  // 30% volume
}
```

## Requirements

- Python 3.6+
- [watchdog](https://pypi.org/project/watchdog/)
- [pygame](https://pypi.org/project/pygame/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Inspired by the need to know when builds and tasks are complete without constant checking
- Thanks to the [watchdog](https://github.com/gorakhargosh/watchdog) library for file system monitoring
- Sound files included are royalty-free 