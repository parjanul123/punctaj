-- Remove granular permissions from discord_users safely
-- Project: yzlkgifumrwqlfgimcai
-- Run this in Supabase SQL Editor

BEGIN;

-- 1) Optional backup of current granular permissions (recommended)
CREATE TABLE IF NOT EXISTS public.discord_users_granular_backup AS
SELECT
    id,
    discord_id,
    username,
    granular_permissions,
    NOW() AS backup_created_at
FROM public.discord_users
WHERE granular_permissions IS NOT NULL;

-- 2) Remove granular permissions column
ALTER TABLE public.discord_users
    DROP COLUMN IF EXISTS granular_permissions;

-- 3) Optional: update table comment to reflect new purpose
COMMENT ON TABLE public.discord_users IS 'Utilizatori autentificați prin Discord (fără permisiuni granulare)';

COMMIT;

-- Verify structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'discord_users'
ORDER BY ordinal_position;
