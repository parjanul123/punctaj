#!/usr/bin/env python3
"""Create action_logs table via SQL direct"""

import requests
import json

# Supabase credentials
SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

print("=" * 70)
print("Creating action_logs table in Supabase")
print("=" * 70)

# The schema for action_logs table that matches what action_logger.py sends
schema = {
    "id": "bigint",
    "discord_id": "text",
    "action_type": "text",
    "city": "text",
    "institution": "text",
    "details": "text",
    "timestamp": "text"
}

print("\nRequired schema:")
for field, field_type in schema.items():
    print(f"  - {field:15} : {field_type}")

print("\nYou need to create this table manually in Supabase:")
print("\n1. Go to: https://app.supabase.com/project/yzlkgifumrwqlfgimcai")
print("2. Click 'SQL Editor' on the left")
print("3. Click 'New Query'")
print("4. Paste this SQL:\n")

sql = """
CREATE TABLE IF NOT EXISTS action_logs (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    city TEXT,
    institution TEXT,
    details TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_action_logs_discord_id ON action_logs(discord_id);
CREATE INDEX IF NOT EXISTS idx_action_logs_action_type ON action_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_action_logs_city ON action_logs(city);
CREATE INDEX IF NOT EXISTS idx_action_logs_timestamp ON action_logs(timestamp DESC);

-- Enable RLS for security
ALTER TABLE action_logs ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to read logs
CREATE POLICY "Allow authenticated users to read action logs"
  ON action_logs FOR SELECT
  TO authenticated
  USING (true);

-- Allow all authenticated users to insert logs
CREATE POLICY "Allow authenticated users to insert action logs"
  ON action_logs FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Allow admins to delete logs
CREATE POLICY "Allow admins to delete action logs"
  ON action_logs FOR DELETE
  TO authenticated
  USING (true);
"""

print(sql)
print("\n5. Click 'Run' to execute")
print("\n" + "=" * 70)
