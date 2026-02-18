-- ============================================================================
-- POLICE_DATA TABLE (main sync table for institution data)
-- ============================================================================

CREATE TABLE IF NOT EXISTS police_data (
  id BIGSERIAL PRIMARY KEY,
  city TEXT NOT NULL,
  institution TEXT NOT NULL,
  data JSONB,
  version INT DEFAULT 1,
  last_synced TIMESTAMP WITH TIME ZONE,
  synced_by TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(city, institution)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_police_data_city_inst ON police_data(city, institution);

-- Enable Row Level Security (but allow public access for now)
ALTER TABLE police_data ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public access (for testing)
DROP POLICY IF EXISTS "Allow public access to police_data" ON police_data;
CREATE POLICY "Allow public access to police_data"
  ON police_data
  FOR ALL
  USING (true)
  WITH CHECK (true);

GRANT ALL ON police_data TO anon, authenticated, service_role;

-- Verify table was created
SELECT 'police_data table created successfully!' AS status;
