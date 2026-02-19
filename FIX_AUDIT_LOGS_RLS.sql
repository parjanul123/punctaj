-- 🔧 FIX: Ensure audit_logs table is fully accessible

-- 1. Check current RLS status
SELECT relname, relrowsecurity 
FROM pg_class 
WHERE relname = 'audit_logs';

-- 2. Ensure RLS is disabled
ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

-- 3. Remove ANY policies that might exist
DROP POLICY IF EXISTS "Enable read access for all users" ON audit_logs;
DROP POLICY IF EXISTS "Enable insert access for all users" ON audit_logs;
DROP POLICY IF EXISTS "Enable update access for all users" ON audit_logs;
DROP POLICY IF EXISTS "Enable delete access for all users" ON audit_logs;
DROP POLICY IF EXISTS "Allow all" ON audit_logs;

-- 4. Verify table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'audit_logs' 
ORDER BY ordinal_position;

-- 5. Count logs in table
SELECT COUNT(*) as total_logs FROM audit_logs;

-- 6. Show last 5 logs
SELECT id, timestamp, action_type, discord_username, details 
FROM audit_logs 
ORDER BY timestamp DESC 
LIMIT 5;

-- 7. Check if there are logs from today (2026-02-19)
SELECT COUNT(*) as logs_today 
FROM audit_logs 
WHERE DATE(timestamp) = '2026-02-19'::date;

-- 8. Show logs from today
SELECT id, timestamp, action_type, discord_username, details 
FROM audit_logs 
WHERE DATE(timestamp) = '2026-02-19'::date
ORDER BY timestamp DESC;
