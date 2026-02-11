-- Create permission_changes table in Supabase for dedicated permission logging
CREATE TABLE IF NOT EXISTS permission_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  discord_id TEXT NOT NULL,
  discord_username TEXT,
  target_user TEXT NOT NULL,
  permission_changes JSONB DEFAULT '{}'::jsonb,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_permission_changes_discord_id ON permission_changes(discord_id);
CREATE INDEX IF NOT EXISTS idx_permission_changes_timestamp ON permission_changes(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_permission_changes_target_user ON permission_changes(target_user);

-- Enable RLS if needed
ALTER TABLE permission_changes ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to view all permission changes
CREATE POLICY "allow_view_permission_changes" ON permission_changes
  FOR SELECT
  TO authenticated
  USING (true);

-- Create policy for allowing inserts from authenticated users
CREATE POLICY "allow_insert_permission_changes" ON permission_changes
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Grant permissions to authenticated users
GRANT SELECT, INSERT ON permission_changes TO authenticated;

-- Add comment to table
COMMENT ON TABLE permission_changes IS 'Logs all permission changes made by admins to users - tracks who gave what permissions to whom';
