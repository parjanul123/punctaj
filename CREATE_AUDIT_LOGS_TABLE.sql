-- Dedicated setup for audit logs table
-- Safe to run multiple times

BEGIN;

CREATE TABLE IF NOT EXISTS public.audit_logs (
  id BIGSERIAL PRIMARY KEY,
  discord_id VARCHAR(255),
  action_type VARCHAR(100),
  city VARCHAR(255),
  institution VARCHAR(255),
  details TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure timezone-aware timestamps on existing tables too
ALTER TABLE public.audit_logs
  ALTER COLUMN timestamp TYPE TIMESTAMPTZ USING timestamp,
  ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at;

-- Extra columns used by app logging
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS discord_username VARCHAR(255) DEFAULT 'unknown';
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS entity_name VARCHAR(255);
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS entity_id VARCHAR(255);
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS changes TEXT;
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS server_key VARCHAR(255);

-- Access / policies
ALTER TABLE public.audit_logs DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Enable read access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Enable insert access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Enable update access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Enable delete access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Allow all" ON public.audit_logs;

GRANT INSERT, SELECT, UPDATE, DELETE ON public.audit_logs TO anon, authenticated, service_role;

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_discord_username ON public.audit_logs(discord_username);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON public.audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_server_key ON public.audit_logs(server_key);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON public.audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON public.audit_logs(action_type);

COMMIT;

-- Optional quick check:
-- SELECT COUNT(*) FROM public.audit_logs;
