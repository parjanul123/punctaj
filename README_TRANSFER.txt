# Punctaj Manager - Transfer Package

## How to use on another device:

1. Extract this ZIP file to any location
   Example: C:\Users\YourName\Punctaj

2. Run punctaj.exe directly
   - Double-click punctaj.exe
   - Or open Command Prompt and type: punctaj.exe

3. On first run:
   - Login with your Discord account
   - Allow Windows (SmartScreen might warn)
   - Wait for database to load

## What's included:

- punctaj.exe          - Ready to run (from dist/)
- supabase_config.ini  - Database connection config
- discord_config.ini   - Discord authentication setup
- data/                - Application data
- dist/                - Backup of exe and dependencies

## If database doesn't load:

Run diagnostic:
  py DIAGNOSE_SUPABASE.py

Run fix:
  py FIX_SUPABASE_CONFIG.py

## Multi-Device Sync:

All devices using same Discord account will:
✅ Share the same database
✅ Have same permissions
✅ Keep data in sync
✅ Fresh login each session (for security)

## Files to keep synchronized:

- supabase_config.ini  - Must be identical on all devices
- discord_config.ini   - Must be identical on all devices

If you change config on one device, copy updated files to other devices.

---
Transfer Date: 2026-02-06 20:42:21
Package Size: Ready to extract anywhere
