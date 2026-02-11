-- Add the new columns for detailed audit logging
ALTER TABLE audit_logs
ADD COLUMN discord_username VARCHAR(255) DEFAULT 'unknown',
ADD COLUMN entity_name VARCHAR(255),
ADD COLUMN entity_id VARCHAR(255),
ADD COLUMN changes TEXT;

-- Add indexes for better query performance
CREATE INDEX idx_audit_logs_discord_username ON audit_logs(discord_username);
CREATE INDEX idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Verify columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'audit_logs' 
ORDER BY ordinal_position;
