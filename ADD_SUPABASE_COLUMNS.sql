-- Add missing columns to audit_logs table in Supabase
-- Run this in Supabase SQL Editor: https://app.supabase.com/project/yzlkgifumrwqlfgimcai/sql/new

-- Add the new columns if they don't exist
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS discord_username TEXT DEFAULT 'unknown',
ADD COLUMN IF NOT EXISTS entity_name TEXT,
ADD COLUMN IF NOT EXISTS entity_id TEXT,
ADD COLUMN IF NOT EXISTS changes TEXT;

-- Optional: Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_discord_username ON audit_logs(discord_username);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_logs(action_type);

-- Verify columns were added
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'audit_logs' 
ORDER BY ordinal_position;
