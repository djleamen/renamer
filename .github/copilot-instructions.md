# GitHub Copilot Instructions for MP3 Renamer

## Project Overview

MP3 Renamer is a Python-based CLI tool that automatically renames MP3 files based on their speech content using AI-powered Speech-to-Text technology. The tool uses OpenAI's Whisper model as the primary transcription engine with Google Speech API as a fallback.

## Project Structure

- `mp3_renamer.py` - Main application script with all core functionality
- `run_mac_fix.py` - Helper script for fixing SSL certificate issues on macOS
- `requirements.txt` - Python dependencies
- `.github/workflows/` - CI/CD workflows including Python linting and testing

## Technology Stack

- **Language**: Python 3.6+
- **Key Dependencies**:
  - `openai-whisper` - Primary speech-to-text engine
  - `torch` - Required for Whisper models
  - `SpeechRecognition` - Fallback speech recognition
  - `pydub` - Audio file manipulation
  - `PyAudio` - Audio processing
- **External Tools**: FFmpeg (for MP3 conversion)

## Coding Standards

### Python Style
- Follow PEP 8 style guidelines
- Maximum line length: 127 characters (as configured in flake8)
- Maximum complexity: 10 (as configured in flake8)
- Use meaningful variable names and add docstrings to functions
- Maintain existing code structure and patterns

### Linting
- Use `flake8` for linting
- Critical errors (E9, F63, F7, F82) must be fixed
- Run linting before committing: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`

### Testing
- Use `pytest` as the testing framework
- Currently no tests exist - when adding tests, follow pytest conventions
- Tests should be placed in a `tests/` directory
- Install test dependencies: `pip install pytest`

## Development Workflow

### Setup
1. Install system dependencies:
   - **Linux**: `apt-get install portaudio19-dev ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download FFmpeg from ffmpeg.org
2. Install Python dependencies: `pip install -r requirements.txt`
3. For macOS SSL issues, use: `python run_mac_fix.py` instead of running `mp3_renamer.py` directly

### Making Changes
1. Ensure changes maintain backward compatibility with Python 3.6+
2. Test with different Whisper models (tiny, base, small, medium, large)
3. Validate audio processing works with various MP3 formats
4. Run flake8 before committing changes
5. Update documentation if adding new features or changing behavior

### Key Functions and Components
- `convert_mp3_to_wav()` - Converts MP3 files to WAV format for processing
- `transcribe_audio()` - Main transcription function with Whisper/Google fallback
- `transcribe_with_whisper()` - Whisper-specific transcription logic
- `extract_first_sentence()` - Extracts meaningful text from transcription
- `clean_filename()` - Sanitizes text for use as filenames
- `process_mp3_files()` - Main orchestration function

## Important Considerations

### Audio Processing
- Always clean up temporary WAV files after processing
- Handle audio duration edge cases (files shorter than requested duration)
- Normalize audio before transcription for better results

### Error Handling
- Gracefully handle transcription failures with fallback mechanisms
- Provide helpful error messages when FFmpeg is not installed
- Handle file permission issues when renaming files

### Performance
- Consider memory usage when loading Whisper models
- Smaller models (tiny, base) are faster but less accurate
- Larger models (medium, large) are more accurate but resource-intensive

### Security
- Never commit API keys or credentials
- Be cautious with file system operations (renaming, deleting)
- Validate and sanitize all user inputs, especially file paths

## Dependencies Management

- Keep dependencies up to date for security patches
- Minimum versions specified in `requirements.txt`
- Test compatibility when updating major dependencies (especially torch and whisper)
- PyAudio requires PortAudio system library - document installation per platform

## Documentation

- Update `README.md` when adding new command-line options
- Document any new dependencies in both README and requirements.txt
- Include usage examples for new features
- Maintain troubleshooting section in README for common issues

## CI/CD

- GitHub Actions workflow runs on push/PR to main branch
- Pipeline includes:
  1. Install system dependencies (PortAudio)
  2. Set up Python 3.10
  3. Install Python dependencies
  4. Run flake8 linting
  5. Run pytest (currently no tests, but framework is ready)
- All checks must pass before merging

## Common Tasks

### Adding a New Feature
1. Implement the feature maintaining existing code patterns
2. Add command-line argument if needed (use argparse)
3. Update help text and documentation
4. Test with different audio files and configurations
5. Run linting to ensure code quality
6. Update README with usage examples

### Fixing a Bug
1. Understand the issue and reproduce it
2. Make minimal changes to fix the issue
3. Ensure the fix doesn't break existing functionality
4. Add verbose logging if helpful for debugging
5. Test with edge cases

### Optimizing Performance
1. Profile the code to identify bottlenecks
2. Consider caching Whisper models to avoid reloading
3. Optimize audio chunk processing
4. Balance accuracy vs. speed based on user's model choice
