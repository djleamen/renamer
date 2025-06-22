"""
Helper script to fix SSL certificate issues on macOS and run the MP3 renamer.

This script:
1. Applies SSL certificate fixes for macOS
2. Runs the MP3 renamer with the specified arguments
"""

import os
import sys
import subprocess
import platform

def fix_mac_ssl():
    """Apply SSL certificate fixes specifically for macOS."""
    if platform.system() != 'Darwin':
        print("This script is only needed on macOS.")
        return True
    
    print("Applying SSL certificate fixes for macOS...")
    
    # Try to install certifi
    try:
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
        print(f"Using certificates from: {certifi.where()}")
    except ImportError:
        print("Installing certifi package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "certifi"])
        try:
            import certifi
            os.environ['SSL_CERT_FILE'] = certifi.where()
            print(f"Using certificates from: {certifi.where()}")
        except ImportError:
            print("Failed to install certifi package.")
    
    # Look for Install Certificates.command
    cert_script_paths = [
        "/Applications/Python 3.*/Install Certificates.command",
        "/Applications/Python/*/Install Certificates.command",
        os.path.expanduser("~/Library/Python/*/bin/Install Certificates.command")
    ]
    
    import glob
    found_script = False
    for path_pattern in cert_script_paths:
        cert_scripts = glob.glob(path_pattern)
        if cert_scripts:
            found_script = True
            print(f"Running certificate installation script: {cert_scripts[0]}")
            result = subprocess.run(['bash', cert_scripts[0]], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
            if result.returncode == 0:
                print("Certificate installation successful")
            else:
                print("Certificate installation may have had issues")
            break
    
    if not found_script:
        print("Could not find certificate installation script.")
        print("As a last resort, using SSL verification bypass (not secure)")
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
    
    return True

def main():
    # Apply SSL fixes
    fix_mac_ssl()
    
    # Get all command line arguments except the script name
    args = sys.argv[1:]
    
    # If no arguments provided, show help
    if not args:
        print("\nUsage examples:")
        print("  python run_mac_fix.py /path/to/mp3/folder")
        print("  python run_mac_fix.py /path/to/mp3/folder --model tiny")
        print("  python run_mac_fix.py /path/to/mp3/folder --engine google")
        print("\nThis script fixes SSL certificate issues on macOS and then runs the MP3 renamer.")
        return
    
    # Construct the command to run the main script
    cmd = [sys.executable, "mp3_renamer.py"] + args
    
    print("\nRunning MP3 renamer with fixed certificates...")
    print(f"Command: {' '.join(cmd)}")
    
    # Execute the MP3 renamer script
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
