#!/usr/bin/env python3
"""
Extract debug from EXE by patching to write logs to file
"""
import subprocess
import time
import os

# Create a wrapper script that patches punctaj.py to log to file
wrapper = r"""
import sys
import os

# Redirect stdout/stderr to file
log_file = r"d:\punctaj\exe_output.log"
class DualWriter:
    def __init__(self, console, file_handle):
        self.console = console
        self.file = file_handle
    def write(self, msg):
        self.console.write(msg)
        self.file.write(msg)
        self.file.flush()
    def flush(self):
        self.console.flush()
        self.file.flush()

f = open(log_file, 'w', encoding='utf-8')
sys.stdout = DualWriter(sys.__stdout__, f)
sys.stderr = DualWriter(sys.__stderr__, f)

# Now run the actual app
exec(open(r'd:\punctaj\dist\punctaj.exe').read())
"""

print("Starting EXE with log capture...")
print("Waiting 15 seconds...")

# Run EXE directly
os.startfile(r"d:\punctaj\dist\punctaj.exe")
time.sleep(15)

log_file = r"d:\punctaj\exe_output.log"
if os.path.exists(log_file):
    print("\n" + "="*70)
    print("EXE OUTPUT LOG:")
    print("="*70 + "\n")
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read())
else:
    print(f"Log file not created at {log_file}")
