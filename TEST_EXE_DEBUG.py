#!/usr/bin/env python3
"""
Test EXE Discord auth with captured output
"""
import subprocess
import time
import os
from pathlib import Path

# Dynamic paths - works on any drive
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
log_file = BASE_DIR / "exe_debug.log"

print("Starting EXE with output capture...")
print(f"Log file: {log_file}")

# Run EXE with output redirect
with open(log_file, 'w', encoding='utf-8') as f:
    process = subprocess.Popen(
        [str(BASE_DIR / "dist" / "punctaj.exe")],
        stdout=f,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print(f"EXE started (PID: {process.pid})")
    print("Wait 10 seconds then close the application...")
    print()

# Keep process running for testing
time.sleep(10)

# Kill process
try:
    process.terminate()
    process.wait(timeout=5)
except:
    process.kill()

print("\nDone! Reading log file...")
print("=" * 70)

if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
else:
    print("Log file not found!")
