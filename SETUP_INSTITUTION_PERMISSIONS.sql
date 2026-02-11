-- ========================================
-- SQL pentru Configurarea Permisiuni Granulare
-- ========================================
-- Rulează aceste comenzi în Supabase SQL Editor

-- 1. Adaugă coloana granular_permissions dacă nu există
ALTER TABLE discord_users 
ADD COLUMN IF NOT EXISTS granular_permissions JSONB DEFAULT '{"institutions": {}}'::jsonb;

-- 2. Set default value pentru utilizatorii existenți (opțional)
UPDATE discord_users 
SET granular_permissions = '{"institutions": {}}'::jsonb 
WHERE granular_permissions IS NULL;

-- ========================================
-- Index pentru Performance (opțional dar recomandat)
-- ========================================
CREATE INDEX IF NOT EXISTS idx_discord_users_granular_perms 
ON discord_users USING gin(granular_permissions);

-- ========================================
-- Exemplu: Setare Permisiuni Manual (pentru testing)
-- ========================================

-- Exemplu 1: Șerif Blackwater - acces la Politie
UPDATE discord_users 
SET granular_permissions = jsonb_set(
  granular_permissions,
  '{institutions, Blackwater, Politie}',
  '{"can_view": true, "can_edit": true, "can_delete": true}'::jsonb
)
WHERE discord_id = '123456';  -- Înlocuiți cu ID-ul real

-- Exemplu 2: Același șerif - fără acces la Medical
UPDATE discord_users 
SET granular_permissions = jsonb_set(
  granular_permissions,
  '{institutions, Blackwater, Medical}',
  '{"can_view": false, "can_edit": false, "can_delete": false}'::jsonb
)
WHERE discord_id = '123456';

-- Exemplu 3: Officer Saint-Denis - acces limitat la Politie
UPDATE discord_users 
SET granular_permissions = jsonb_set(
  granular_permissions,
  '{institutions, Saint-Denis, Politie}',
  '{"can_view": true, "can_edit": false, "can_delete": false}'::jsonb
)
WHERE discord_id = '789012';  -- Înlocuiți cu ID-ul real

-- ========================================
-- Verificare: Afișează Permisiuni unui Utilizator
-- ========================================

-- Vizualizare structura JSON
SELECT 
  discord_id,
  username,
  granular_permissions
FROM discord_users
WHERE discord_id = '123456';

-- Extrage doar instituțiile
SELECT 
  discord_id,
  username,
  granular_permissions -> 'institutions' AS institutions
FROM discord_users
WHERE discord_id = '123456';

-- Extrage o instituție specifică
SELECT 
  discord_id,
  username,
  granular_permissions -> 'institutions' -> 'Blackwater' -> 'Politie' AS blackwater_police
FROM discord_users
WHERE discord_id = '123456';

-- ========================================
-- Queryuri Utile
-- ========================================

-- Toți utilizatorii cu acces la Blackwater
SELECT 
  discord_id,
  username,
  granular_permissions -> 'institutions' -> 'Blackwater' AS blackwater_access
FROM discord_users
WHERE granular_permissions -> 'institutions' -> 'Blackwater' IS NOT NULL;

-- Utilizatori cu acces complet (view + edit + delete) la o instituție
SELECT 
  discord_id,
  username
FROM discord_users
WHERE 
  granular_permissions -> 'institutions' -> 'Blackwater' -> 'Politie' ->> 'can_view' = 'true'
  AND granular_permissions -> 'institutions' -> 'Blackwater' -> 'Politie' ->> 'can_edit' = 'true'
  AND granular_permissions -> 'institutions' -> 'Blackwater' -> 'Politie' ->> 'can_delete' = 'true';

-- ========================================
-- RLS Policy - Securitate (Opțional)
-- ========================================

-- IMPORTANT: Activează RLS pe tabela discord_users
-- ALTER TABLE discord_users ENABLE ROW LEVEL SECURITY;

-- Policy: Doar superuser poate modifica granular_permissions
-- CREATE POLICY "superuser_can_manage_permissions" ON discord_users
-- FOR UPDATE
-- USING (
--   (SELECT is_superuser FROM discord_users WHERE id = auth.uid()) = true
-- )
-- WITH CHECK (
--   (SELECT is_superuser FROM discord_users WHERE id = auth.uid()) = true
-- );

-- Policy: Utilizatorii pot vedea doar propriile permisiuni
-- CREATE POLICY "users_see_own_permissions" ON discord_users
-- FOR SELECT
-- USING (
--   id = auth.uid() OR
--   (SELECT is_superuser FROM discord_users WHERE id = auth.uid()) = true
-- );

-- ========================================
-- Ștergere Date (DANGER - pentru testing only)
-- ========================================

-- Resetează permisiuni pentru un utilizator
-- UPDATE discord_users 
-- SET granular_permissions = '{"institutions": {}}'::jsonb
-- WHERE discord_id = '123456';

-- Resetează pentru toți utilizatorii
-- UPDATE discord_users 
-- SET granular_permissions = '{"institutions": {}}'::jsonb;
