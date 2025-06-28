# MP3 Renamer

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/djleamen/renamer)](LICENSE)
![Status](https://img.shields.io/badge/status-active-brightgreen)
[![Last Commit](https://img.shields.io/github/last-commit/djleamen/renamer)](https://github.com/djleamen/renamer/commits)

A Python tool that automatically renames MP3 files based on their speech content using AI-powered Speech-to-Text technology.

## Features

- Scans a directory for MP3 files
- Converts each MP3 to WAV format (temporarily)
- Uses OpenAI's Whisper model for high-quality transcription (with Google Speech API as fallback)
- Extracts the first sentence or a specified number of words from the transcription
- Renames the MP3 file based on this extracted text
- Cleans filenames to ensure they are valid

## Requirements

- Python 3.6 or later
- Required Python packages (install with `pip install -r requirements.txt`):
  - openai-whisper (for state-of-the-art speech recognition)
  - torch (required for Whisper)
  - SpeechRecognition (fallback recognition)
  - pydub (audio file manipulation)
  - PyAudio (for audio processing)
  - ffmpeg-python (for audio conversion)
- FFmpeg (for MP3 conversion)

## Installation

1. Clone or download this repository
2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```
3. Install FFmpeg (if not already installed):
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

### Basic Usage

Run the script with the path to the directory containing MP3 files:

```bash
python mp3_renamer.py /path/to/mp3/folder
```

### Advanced Options

```bash
python mp3_renamer.py /path/to/mp3/folder [options]
```

Available options:

- `-d, --duration SECONDS` - Process only a specific duration (default: 10 seconds)
- `-s, --start SECONDS` - Start processing from this time (default: 0 seconds)
- `-f, --first N` - Use the first N words for the filename instead of a sentence
- `-v, --verbose` - Enable verbose output for debugging
- `-e, --engine {whisper,google,both}` - Choose the speech recognition engine (default: whisper)
- `-m, --model {tiny,base,small,medium,large}` - Select Whisper model size (default: base)

### Examples

Use Whisper with a larger model for better accuracy:

```bash
python mp3_renamer.py /path/to/mp3/folder --model medium
```

Process only the first 5 seconds of each file:

```bash
python mp3_renamer.py /path/to/mp3/folder --duration 5
```

Use the first 10 words instead of trying to detect a sentence:

```bash
python mp3_renamer.py /path/to/mp3/folder --first 10
```

## How It Works

1. The script scans the specified directory for MP3 files
2. For each MP3 file:
   - Converts it to WAV format (needed for speech recognition)
   - Uses OpenAI's Whisper model to transcribe the audio
   - Extracts the first sentence or specified number of words
   - Cleans the text to make it a valid filename
   - Renames the MP3 file with the new name
   - Removes the temporary WAV file

## Choosing a Whisper Model

- `tiny`: Fastest, lowest accuracy, minimal resource usage
- `base`: Good balance of speed and accuracy (default)
- `small`: Better accuracy, moderate resource usage
- `medium`: High accuracy, higher resource usage
- `large`: Best accuracy, significant resource usage

## Troubleshooting

If you encounter issues:

1. Try running with `--verbose` to see detailed logs
2. Use `--model small` or `--model medium` for better transcription
3. Adjust the `--start` and `--duration` parameters to capture the correct part of audio
4. Use `--first N` to bypass sentence detection if it's not working well
