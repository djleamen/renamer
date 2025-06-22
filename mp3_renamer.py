"""
MP3 Renamer - A tool to automatically rename MP3 files based on their speech content.
"""
import os
import sys
import argparse
import speech_recognition as sr
import pydub
from pathlib import Path
from pydub import AudioSegment
import re
import string
import torch
import whisper
import tempfile

VERBOSE = False
WHISPER_MODEL = None

def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.with_suffix('.wav')
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio(wav_path, duration=10, start_time=0, use_whisper=True):
    if use_whisper:
        whisper_result = transcribe_with_whisper(wav_path, duration, start_time)
        if whisper_result:
            if VERBOSE:
                print(f"  Whisper transcription: {whisper_result}")
            return whisper_result
        else:
            print("  Whisper transcription failed. Falling back to Google Speech Recognition.")
    recognizer = sr.Recognizer()
    audio_data = AudioSegment.from_file(str(wav_path))
    start_ms = int(start_time * 1000)
    duration_ms = int(duration * 1000)
    if start_ms < len(audio_data):
        end_ms = min(start_ms + duration_ms, len(audio_data))
        audio_data = audio_data[start_ms:end_ms]
    normalized_audio = audio_data.normalize()
    temp_wav_path = wav_path.with_name(f"temp_{wav_path.name}")
    normalized_audio.export(temp_wav_path, format="wav")
    with sr.AudioFile(str(temp_wav_path)) as source:
        recognizer.energy_threshold = 300
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio, language="en-US", show_all=False)
        if VERBOSE:
            print(f"  Google transcription: {transcript}")
        os.remove(temp_wav_path)
        return transcript
    except sr.UnknownValueError:
        print(f"  Google Speech recognition could not understand the audio in {wav_path.name}")
        os.remove(temp_wav_path)
        return None
    except sr.RequestError as e:
        print(f"  Could not request results from Google speech recognition service; {e}")
        os.remove(temp_wav_path)
        return None
    except Exception as e:
        print(f"  An error occurred during Google transcription: {e}")
        if temp_wav_path.exists():
            os.remove(temp_wav_path)
        return None

def extract_first_sentence(text):
    if not text:
        return None
    text = ' '.join(text.split())
    sentence_patterns = [
        r'([.!?])\s+[A-Z]',
        r'([.!?])\s+',
        r'([.!?])'
    ]
    for pattern in sentence_patterns:
        match = re.search(pattern, text)
        if match:
            end_pos = match.start() + 1
            return text[:end_pos].strip()
    natural_breaks = [
        r'(,\s+)',
        r'(\s+and\s+)',
        r'(\s+but\s+)',
        r'(\s+so\s+)',
    ]
    for pattern in natural_breaks:
        match = re.search(pattern, text)
        if match and match.start() > 10:
            return text[:match.start()].strip()
    words = text.split()
    if len(words) > 12:
        return ' '.join(words[:12]).strip() + '...'
    return text[:min(len(text), 50)].strip()

def clean_filename(text):
    if not text:
        return "untranscribable"
    text = text.strip()
    text = re.sub(r'[.!?]+$', '', text)
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned = ''.join(c if c in valid_chars else '_' for c in text)
    cleaned = re.sub(r'_+', '_', cleaned)
    cleaned = cleaned.strip('_')
    if len(cleaned) > 100:
        cleaned = cleaned[:97] + '...'
    if not cleaned:
        return "untranscribable"
    return cleaned

def rename_mp3_file(mp3_path, new_name):
    try:
        new_path = mp3_path.parent / f"{new_name}{mp3_path.suffix}"
        mp3_path.rename(new_path)
        return new_path
    except Exception as e:
        print(f"Error renaming {mp3_path.name}: {e}")
        return mp3_path

def process_mp3_file(mp3_path, duration=10, start_time=0, first_n_words=None, use_whisper=True):
    print(f"Processing: {mp3_path}")
    wav_path = convert_mp3_to_wav(mp3_path)
    if VERBOSE:
        print(f"  Converted to WAV for processing")
    if VERBOSE:
        print(f"  Transcribing audio from {start_time}s for {duration}s using {'Whisper' if use_whisper else 'Google Speech API'}...")
    transcript = transcribe_audio(wav_path, duration, start_time, use_whisper)
    if transcript:
        if VERBOSE:
            print(f"  Full transcript: \"{transcript}\"")
    else:
        print(f"  Failed to transcribe audio")
    if first_n_words is not None and transcript:
        words = transcript.split()
        if len(words) > first_n_words:
            first_sentence = ' '.join(words[:first_n_words])
        else:
            first_sentence = transcript
    else:
        first_sentence = extract_first_sentence(transcript)
    if VERBOSE:
        print(f"  Extracted text for filename: \"{first_sentence}\"")
    new_name = clean_filename(first_sentence)
    if VERBOSE:
        print(f"  Cleaned filename: \"{new_name}\"")
    os.remove(wav_path)
    if not new_name or new_name == "untranscribable":
        print(f"  Could not transcribe: {mp3_path.name}")
        return mp3_path
    new_path = rename_mp3_file(mp3_path, new_name)
    print(f"  Renamed to: {new_path.name}")
    return new_path

def process_directory(directory_path, duration=10, start_time=0, first_n_words=None, use_whisper=True):
    directory = Path(directory_path).resolve()
    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist or is not a directory")
        return
    mp3_files = list(directory.glob('*.mp3'))
    if not mp3_files:
        print(f"No MP3 files found in {directory}")
        return
    print(f"Found {len(mp3_files)} MP3 file(s) to process")
    for mp3_file in mp3_files:
        process_mp3_file(mp3_file, duration, start_time, first_n_words, use_whisper)
    print("Processing complete!")

def init_whisper_model(model_size="base"):
    global WHISPER_MODEL
    print(f"Loading Whisper {model_size} model...")
    try:
        try:
            import torch
            print(f"PyTorch version: {torch.__version__}")
            if torch.cuda.is_available():
                print(f"CUDA available: Yes (Device: {torch.cuda.get_device_name(0)})")
            else:
                print("CUDA available: No, using CPU mode")
        except ImportError:
            print("PyTorch not properly installed. This is required for Whisper.")
            print("Try reinstalling with: pip install torch")
            return None
        print(f"Downloading/loading the Whisper {model_size} model...")
        print("This may take a few minutes on first run as the model is downloaded.")
        print("Models are downloaded to ~/.cache/whisper/ by default")
        WHISPER_MODEL = whisper.load_model(model_size)
        print(f"Whisper {model_size} model loaded successfully")
        return WHISPER_MODEL
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
            print("\nSSL Certificate error detected.")
            print("This is a common issue on macOS Python installations.")
            print("\nTry these solutions:")
            print("1. Install certifi package: pip install certifi")
            print("2. Run: /Applications/Python*/Install\\ Certificates.command")
            print("3. Use --engine google to use Google Speech Recognition instead")
            print("4. See more macOS SSL solutions at: https://stackoverflow.com/questions/27835619/")
        print("\nGeneral troubleshooting steps:")
        print("1. Ensure you have the required packages installed:")
        print("   pip install --upgrade openai-whisper torch certifi")
        print("2. Try using a smaller model: --model tiny")
        print("3. If on Windows, ensure you have Microsoft Visual C++ Redistributable installed")
        print("4. Ensure ffmpeg is installed on your system:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu: apt-get install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
        print("5. As a temporary workaround, try using: --engine google")
        return None

def transcribe_with_whisper(audio_path, duration=10, start_time=0):
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        print("Whisper model not initialized, attempting to load now...")
        init_whisper_model()
        if WHISPER_MODEL is None:
            print("Could not initialize Whisper model")
            print("This could be due to:")
            print("1. Missing dependencies (torch, ffmpeg)")
            print("2. Insufficient system resources")
            print("3. Permission issues accessing model files")
            print("\nTry using --engine google instead")
            return None
    try:
        if start_time > 0 or duration < float('inf'):
            audio_data = AudioSegment.from_file(str(audio_path))
            start_ms = int(start_time * 1000)
            duration_ms = int(duration * 1000)
            if start_ms < len(audio_data):
                end_ms = min(start_ms + duration_ms, len(audio_data))
                audio_data = audio_data[start_ms:end_ms]
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                audio_data.export(temp_path, format="wav")
            audio_file_to_transcribe = temp_path
        else:
            audio_file_to_transcribe = audio_path
        if VERBOSE:
            print(f"  Transcribing with Whisper model...")
        result = WHISPER_MODEL.transcribe(
            audio_file_to_transcribe,
            language="en",
            fp16=torch.cuda.is_available()
        )
        if audio_file_to_transcribe != audio_path:
            os.remove(audio_file_to_transcribe)
        return result["text"].strip()
    except Exception as e:
        print(f"Error during Whisper transcription: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None

def check_ffmpeg():
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("ffmpeg is installed and available")
            return True
        else:
            print("Error: ffmpeg check failed with return code", result.returncode)
            return False
    except Exception as e:
        print(f"Error checking ffmpeg: {e}")
        print("ffmpeg may not be installed or not in your PATH")
        return False

def fix_ssl_certificate():
    import platform
    import os
    import subprocess
    if platform.system() == 'Darwin':
        print("Detected macOS, checking for SSL certificate fix...")
        try:
            try:
                import certifi
                os.environ['SSL_CERT_FILE'] = certifi.where()
                print("Using certifi for SSL certificates")
                return True
            except ImportError:
                print("certifi package not found. You can install it with: pip install certifi")
            cert_script_paths = [
                "/Applications/Python 3.*/Install Certificates.command",
                "/Applications/Python/*/Install Certificates.command",
                os.path.expanduser("~/Library/Python/*/bin/Install Certificates.command")
            ]
            for path_pattern in cert_script_paths:
                import glob
                cert_scripts = glob.glob(path_pattern)
                if cert_scripts:
                    print(f"Found certificate installation script: {cert_scripts[0]}")
                    print("Attempting to run certificate fix script...")
                    result = subprocess.run(['bash', cert_scripts[0]], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE)
                    if result.returncode == 0:
                        print("SSL certificate installation successful")
                        return True
            print("WARNING: Could not fix SSL certificates properly.")
            print("As a temporary workaround, will disable SSL verification.")
            print("This is NOT SECURE and should be fixed properly later.")
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            return True
        except Exception as e:
            print(f"Error while trying to fix SSL certificates: {e}")
            print("Will attempt to continue but may encounter SSL errors")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Rename MP3 files based on their speech content"
    )
    parser.add_argument(
        "directory",
        help="Directory containing MP3 files to process"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=10,
        help="Duration in seconds to process (default: 10)"
    )
    parser.add_argument(
        "-s", "--start",
        type=float,
        default=0,
        help="Start time in seconds for audio processing (default: 0)"
    )
    parser.add_argument(
        "-f", "--first",
        type=int,
        default=None,
        help="Process only the first N words from the transcript (overrides sentence extraction)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug output"
    )
    parser.add_argument(
        "-e", "--engine",
        choices=["whisper", "google", "both"],
        default="whisper",
        help="Speech recognition engine to use: whisper, google, or both (default: whisper)"
    )
    parser.add_argument(
        "-m", "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base)"
    )
    args = parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose
    try:
        use_whisper = args.engine in ["whisper", "both"]
        if use_whisper:
            print("\n=== Setting up Whisper speech recognition ===")
            fix_ssl_certificate()
            ffmpeg_available = check_ffmpeg()
            if not ffmpeg_available:
                print("Warning: ffmpeg is required for Whisper but not found.")
                if args.engine == "both":
                    print("Falling back to Google Speech Recognition only.")
                    use_whisper = False
                elif args.engine == "whisper":
                    print("To use Google Speech Recognition instead, run with --engine google")
                    print("Attempting to continue with Whisper, but it may fail...")
            if use_whisper:
                model_loaded = init_whisper_model(args.model)
                if not model_loaded:
                    if args.engine == "both":
                        print("Falling back to Google Speech Recognition.")
                        use_whisper = False
                    elif args.engine == "whisper":
                        print("Cannot continue without Whisper model. Either:")
                        print("1. Fix the installation issues above, or")
                        print("2. Run again with --engine google")
                        return
        print("\n=== Starting MP3 processing ===")
        process_directory(
            args.directory, 
            args.duration, 
            args.start, 
            first_n_words=args.first,
            use_whisper=use_whisper
        )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("If you're having issues with Whisper, try running with --engine google instead")

if __name__ == "__main__":
    fix_ssl_certificate()
    main()
