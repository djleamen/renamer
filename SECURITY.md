# Security Advisory: Python-Future Vulnerability

## Issue Description

This repository previously included a dependency on `ffmpeg-python` version 0.2.0, which has a transitive dependency on `future` version 1.0.0. The Python-Future 1.0.0 module contains a security vulnerability that allows for arbitrary code execution through the unintended import of files named `test.py`.

## Vulnerability Details

- **Package**: future (pip) 
- **Affected Version**: 1.0.0
- **CVE**: Not yet assigned
- **Severity**: High

### Technical Details

The vulnerability exists in `/future/standard_library/__init__.py` at line 491, where there is an unguarded `import test` statement:

```python
# Patch the test module so it appears to have the same structure on Py2 as on Py3
try:
    import test  # <- This line is vulnerable
except ImportError:
    pass
```

When the future module is loaded, it automatically imports any file named `test.py` present in the current working directory or in `sys.path`. An attacker who can write files to the server could exploit this by creating a malicious `test.py` file that would be executed when the application runs.

## Resolution

The vulnerability has been mitigated by removing the unnecessary `ffmpeg-python` dependency from `requirements.txt`. 

### Changes Made

1. **Removed dependency**: `ffmpeg-python>=0.2.0` from `requirements.txt`
2. **Updated documentation**: Clarified that FFmpeg is used by pydub, not through ffmpeg-python
3. **Code analysis**: Confirmed that the application uses `pydub.AudioSegment.from_mp3()` for audio conversion, making ffmpeg-python unnecessary

### Why This Fix Works

- The application never actually imported or used `ffmpeg-python` directly
- Audio conversion is handled by `pydub`, which uses the system FFmpeg binary
- Removing `ffmpeg-python` eliminates the transitive dependency on the vulnerable `future` 1.0.0 package
- No functionality is lost, as the application continues to work with just pydub and system FFmpeg

## Verification

After applying this fix:

1. The vulnerable `future` package is no longer installed as a dependency
2. The application continues to function normally for MP3 to WAV conversion using `pydub.AudioSegment.from_mp3()`
3. No `test.py` files in the working directory can be accidentally executed
4. The attack surface is reduced by eliminating an unnecessary transitive dependency

### Verification Script

A verification script can confirm the mitigation:

```python
# Check that future and ffmpeg-python are not installed
import sys
try:
    import future
    print("❌ FAIL: future package still installed")
except ImportError:
    print("✅ PASS: future package not installed")

try:
    import ffmpeg
    print("❌ FAIL: ffmpeg-python package still installed") 
except ImportError:
    print("✅ PASS: ffmpeg-python package not installed")
```

1. **Keep dependencies minimal**: Only include dependencies that are actually used
2. **Regular security audits**: Use tools like `pip-audit` to check for vulnerable dependencies
3. **Dependency review**: Periodically review and remove unused dependencies

## Additional Information

- FFmpeg must still be installed on the system for pydub to function
- The application's core functionality remains unchanged
- Users should continue to install FFmpeg as documented in the installation instructions

---

**Fixed Date**: January 2025  
**Fixed By**: Automated security remediation