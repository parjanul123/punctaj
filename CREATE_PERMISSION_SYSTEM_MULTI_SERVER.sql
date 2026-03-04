-- Multi-server permission system for RedM
-- Scope permissions by server, city, institution
-- So BlackWater on Server A != BlackWater on Server B

BEGIN;

-- Needed for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Optional safety: ensure login users table exists (used by view)
CREATE TABLE IF NOT EXISTS public.discord_login_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    first_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    login_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 1) Servers registry (tenant boundary)
CREATE TABLE IF NOT EXISTS public.app_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_key TEXT NOT NULL UNIQUE, -- ex: redm_server_1 / discord_guild_id
    server_name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2) Global users (already used by your login flow)
-- Assumes table exists: public.discord_login_users(discord_id, username, ...)

-- 3) Membership per server (same user can exist in many servers)
CREATE TABLE IF NOT EXISTS public.server_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES public.app_servers(id) ON DELETE CASCADE,
    discord_id TEXT NOT NULL,
    username_snapshot TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_server_user UNIQUE (server_id, discord_id)
);

-- Users assigned to server must exist in global login users table (44808)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints tc
        WHERE tc.table_schema = 'public'
          AND tc.table_name = 'server_users'
          AND tc.constraint_name = 'fk_server_users_discord_login_user'
    ) THEN
        ALTER TABLE public.server_users
        ADD CONSTRAINT fk_server_users_discord_login_user
        FOREIGN KEY (discord_id)
        REFERENCES public.discord_login_users(discord_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_server_users_server_id ON public.server_users(server_id);
CREATE INDEX IF NOT EXISTS idx_server_users_discord_id ON public.server_users(discord_id);

-- 3.1) Audit logs table (separate, with server classification)
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    discord_id VARCHAR(255),
    action_type VARCHAR(100),
    city VARCHAR(255),
    institution VARCHAR(255),
    details TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE public.audit_logs DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Enable read access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Enable insert access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Enable update access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Enable delete access for all users" ON public.audit_logs;
DROP POLICY IF EXISTS "Allow all" ON public.audit_logs;

SELECT COUNT(*) FROM public.audit_logs;

GRANT INSERT, SELECT, UPDATE, DELETE ON public.audit_logs TO anon, authenticated, service_role;

-- Add columns only if missing
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS discord_username VARCHAR(255) DEFAULT 'unknown';
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS entity_name VARCHAR(255);
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS entity_id VARCHAR(255);
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS changes TEXT;
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS server_key VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_audit_logs_discord_username ON public.audit_logs(discord_username);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON public.audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_server_key ON public.audit_logs(server_key);

-- 4) Permission catalog
CREATE TABLE IF NOT EXISTS public.app_permissions (
    id BIGSERIAL PRIMARY KEY,
    permission_code TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5) Scoped permissions (SERVER + optional CITY + optional INSTITUTION)
CREATE TABLE IF NOT EXISTS public.user_server_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES public.app_servers(id) ON DELETE CASCADE,
    discord_id TEXT NOT NULL,
    permission_code TEXT NOT NULL REFERENCES public.app_permissions(permission_code) ON DELETE CASCADE,

    -- Optional resource scope
    city_name TEXT,
    institution_name TEXT,

    granted BOOLEAN NOT NULL DEFAULT TRUE,
    granted_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- If institution is set, city must be set
    CONSTRAINT chk_institution_requires_city CHECK (
        institution_name IS NULL OR city_name IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_usp_server_user ON public.user_server_permissions(server_id, discord_id);
CREATE INDEX IF NOT EXISTS idx_usp_server_city_inst ON public.user_server_permissions(server_id, city_name, institution_name);
CREATE INDEX IF NOT EXISTS idx_usp_permission_code ON public.user_server_permissions(permission_code);
CREATE INDEX IF NOT EXISTS idx_usp_granted ON public.user_server_permissions(granted);

-- TRUE uniqueness for nullable scope columns (NULLs are normalized)
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_server_permission_scope_idx
ON public.user_server_permissions (
    server_id,
    discord_id,
    permission_code,
    COALESCE(city_name, ''),
    COALESCE(institution_name, '')
);

-- 6) updated_at trigger helper
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_app_servers_updated_at ON public.app_servers;
CREATE TRIGGER trg_app_servers_updated_at
BEFORE UPDATE ON public.app_servers
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_server_users_updated_at ON public.server_users;
CREATE TRIGGER trg_server_users_updated_at
BEFORE UPDATE ON public.server_users
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_app_permissions_updated_at ON public.app_permissions;
CREATE TRIGGER trg_app_permissions_updated_at
BEFORE UPDATE ON public.app_permissions
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_user_server_permissions_updated_at ON public.user_server_permissions;
CREATE TRIGGER trg_user_server_permissions_updated_at
BEFORE UPDATE ON public.user_server_permissions
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 7) Seed permission catalog
INSERT INTO public.app_permissions (permission_code, display_name, category, description)
VALUES
('can_view', 'Vizualizare date', 'core', 'Acces vizualizare date aplicație'),
('can_edit', 'Editare date', 'core', 'Poate modifica date'),
('can_delete', 'Ștergere date', 'core', 'Poate șterge date'),
('can_add_city', 'Adăugare oraș', 'cities', 'Poate adăuga orașe noi'),
('can_edit_city', 'Editare oraș', 'cities', 'Poate edita orașe existente'),
('can_delete_city', 'Ștergere oraș', 'cities', 'Poate șterge orașe'),
('can_edit_employee', 'Editare angajați', 'employees', 'Poate edita angajați'),
('can_add_employee', 'Adăugare angajați', 'employees', 'Poate adăuga angajați'),
('can_delete_employee', 'Ștergere angajați', 'employees', 'Poate șterge angajați'),
('can_add_institution', 'Adăugare instituții', 'institutions', 'Poate adăuga instituții'),
('can_edit_institution', 'Editare instituții', 'institutions', 'Poate edita instituții'),
('can_delete_institution', 'Ștergere instituții', 'institutions', 'Poate șterge instituții'),
('can_add_score', 'Adăugare punctaj', 'points', 'Poate adăuga punctaj'),
('can_remove_score', 'Scădere punctaj', 'points', 'Poate scădea punctaj'),
('can_reset_score', 'Reset punctaj', 'points', 'Poate reseta punctaj'),
('can_add_cities', 'Adăugare orașe', 'admin', 'Poate adăuga orașe'),
('can_edit_cities', 'Editare orașe', 'admin', 'Poate edita orașe'),
('can_delete_cities', 'Ștergere orașe', 'admin', 'Poate șterge orașe'),
('can_view_logs', 'Vizualizare loguri', 'logs', 'Poate vedea loguri'),
('can_view_activity_logs', 'Vizualizare Activity Logs', 'logs', 'Poate vedea logurile activității'),
('can_view_weekly_report', 'Vizualizare raport săptămânal', 'reports', 'Poate vedea raportul săptămânii trecute'),
('can_manage_user_permissions', 'Gestionare permisiuni useri', 'admin', 'Poate acorda/revoca permisiuni'),
('can_see_user_permissions_button', 'Buton permisiuni useri', 'ui', 'Poate vedea butonul de permisiuni useri'),
('can_see_admin_panel', 'Panou admin', 'ui', 'Poate vedea panoul admin'),
('can_see_admin_button', 'Buton admin', 'ui', 'Poate vedea butonul admin')
ON CONFLICT (permission_code) DO NOTHING;

-- 8) Useful view with server context
CREATE OR REPLACE VIEW public.v_user_server_permissions AS
SELECT
    s.server_key,
    s.server_name,
    usp.discord_id,
    COALESCE(dlu.username, su.username_snapshot) AS username,
    usp.permission_code,
    ap.display_name,
    usp.city_name,
    usp.institution_name,
    usp.granted,
    usp.updated_at,
    COALESCE(dlu.username, su.username_snapshot) AS can_allow
FROM public.user_server_permissions usp
JOIN public.app_servers s ON s.id = usp.server_id
LEFT JOIN public.discord_login_users dlu ON dlu.discord_id = usp.discord_id
LEFT JOIN public.server_users su
       ON su.server_id = usp.server_id
      AND su.discord_id = usp.discord_id
LEFT JOIN public.app_permissions ap ON ap.permission_code = usp.permission_code;

-- Users available for permission assignment in a given server (source: discord_login_users / table 44808)
CREATE OR REPLACE VIEW public.v_permission_assignable_users AS
SELECT
    s.server_key,
    s.server_name,
    su.server_id,
    su.discord_id,
    COALESCE(dlu.username, su.username_snapshot) AS username,
    su.is_active,
    su.created_at,
    su.updated_at
FROM public.server_users su
JOIN public.app_servers s ON s.id = su.server_id
LEFT JOIN public.discord_login_users dlu ON dlu.discord_id = su.discord_id;

-- 9) Delegated permission management (superuser -> delegated managers)

-- Users protected from delegated edits (tu + eventual alți superuseri)
CREATE TABLE IF NOT EXISTS public.server_superusers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES public.app_servers(id) ON DELETE CASCADE,
    discord_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_server_superuser UNIQUE (server_id, discord_id)
);

CREATE INDEX IF NOT EXISTS idx_server_superusers_server_id ON public.server_superusers(server_id);
CREATE INDEX IF NOT EXISTS idx_server_superusers_discord_id ON public.server_superusers(discord_id);

DROP TRIGGER IF EXISTS trg_server_superusers_updated_at ON public.server_superusers;
CREATE TRIGGER trg_server_superusers_updated_at
BEFORE UPDATE ON public.server_superusers
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Cine poate administra permisiunile altora în server
CREATE TABLE IF NOT EXISTS public.permission_admin_delegations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES public.app_servers(id) ON DELETE CASCADE,
    granted_by_discord_id TEXT NOT NULL,
    manager_discord_id TEXT NOT NULL,
    can_grant BOOLEAN NOT NULL DEFAULT TRUE,
    can_revoke BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_permission_admin_delegation UNIQUE (server_id, manager_discord_id)
);

CREATE INDEX IF NOT EXISTS idx_pad_server_manager ON public.permission_admin_delegations(server_id, manager_discord_id);

DROP TRIGGER IF EXISTS trg_permission_admin_delegations_updated_at ON public.permission_admin_delegations;
CREATE TRIGGER trg_permission_admin_delegations_updated_at
BEFORE UPDATE ON public.permission_admin_delegations
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Optional: limitează ce coduri poate acorda/revoca un manager delegat
CREATE TABLE IF NOT EXISTS public.permission_admin_allowed_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delegation_id UUID NOT NULL REFERENCES public.permission_admin_delegations(id) ON DELETE CASCADE,
    permission_code TEXT NOT NULL REFERENCES public.app_permissions(permission_code) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_delegation_permission_code UNIQUE (delegation_id, permission_code)
);

CREATE INDEX IF NOT EXISTS idx_paac_delegation_id ON public.permission_admin_allowed_codes(delegation_id);

-- Helper: actor poate administra target în server?
CREATE OR REPLACE FUNCTION public.can_actor_manage_target(
    p_server_id UUID,
    p_actor_discord_id TEXT,
    p_target_discord_id TEXT,
    p_permission_code TEXT,
    p_action TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_actor_is_superuser BOOLEAN;
    v_target_is_superuser BOOLEAN;
    v_delegation_id UUID;
    v_can_grant BOOLEAN;
    v_can_revoke BOOLEAN;
    v_has_code_limit BOOLEAN;
BEGIN
    IF p_actor_discord_id IS NULL OR p_target_discord_id IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Nimeni nu își poate modifica propriile permisiuni din acest flow
    IF p_actor_discord_id = p_target_discord_id THEN
        RETURN FALSE;
    END IF;

    SELECT EXISTS (
        SELECT 1 FROM public.server_superusers ss
        WHERE ss.server_id = p_server_id AND ss.discord_id = p_actor_discord_id
    ) INTO v_actor_is_superuser;

    SELECT EXISTS (
        SELECT 1 FROM public.server_superusers ss
        WHERE ss.server_id = p_server_id AND ss.discord_id = p_target_discord_id
    ) INTO v_target_is_superuser;

    -- Superuser-ul este protejat: nu poate fi modificat de nimeni (în afară de SQL direct)
    IF v_target_is_superuser THEN
        RETURN FALSE;
    END IF;

    -- Superuser poate administra pe oricine (except superuseri)
    IF v_actor_is_superuser THEN
        RETURN TRUE;
    END IF;

    -- Verifică delegare activă
    SELECT pad.id, pad.can_grant, pad.can_revoke
    INTO v_delegation_id, v_can_grant, v_can_revoke
    FROM public.permission_admin_delegations pad
    WHERE pad.server_id = p_server_id
      AND pad.manager_discord_id = p_actor_discord_id
      AND pad.is_active = TRUE
    LIMIT 1;

    IF v_delegation_id IS NULL THEN
        RETURN FALSE;
    END IF;

    IF p_action = 'grant' AND NOT v_can_grant THEN
        RETURN FALSE;
    END IF;

    IF p_action = 'revoke' AND NOT v_can_revoke THEN
        RETURN FALSE;
    END IF;

    -- Dacă există limitări pe coduri, actorul poate administra doar codurile permise
    SELECT EXISTS (
        SELECT 1
        FROM public.permission_admin_allowed_codes paac
        WHERE paac.delegation_id = v_delegation_id
    ) INTO v_has_code_limit;

    IF v_has_code_limit THEN
        RETURN EXISTS (
            SELECT 1
            FROM public.permission_admin_allowed_codes paac
            WHERE paac.delegation_id = v_delegation_id
              AND paac.permission_code = p_permission_code
        );
    END IF;

    RETURN TRUE;
END;
$$;

-- RPC-like function: grant permission with enforcement
CREATE OR REPLACE FUNCTION public.grant_user_permission(
    p_server_key TEXT,
    p_actor_discord_id TEXT,
    p_target_discord_id TEXT,
    p_permission_code TEXT,
    p_city_name TEXT DEFAULT NULL,
    p_institution_name TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_id UUID;
BEGIN
    SELECT id INTO v_server_id
    FROM public.app_servers
    WHERE server_key = p_server_key
    LIMIT 1;

    IF v_server_id IS NULL THEN
        RETURN FALSE;
    END IF;

    IF NOT public.can_actor_manage_target(v_server_id, p_actor_discord_id, p_target_discord_id, p_permission_code, 'grant') THEN
        RETURN FALSE;
    END IF;

    UPDATE public.user_server_permissions usp
    SET granted = TRUE,
        granted_by = p_actor_discord_id,
        updated_at = NOW()
    WHERE usp.server_id = v_server_id
      AND usp.discord_id = p_target_discord_id
      AND usp.permission_code = p_permission_code
      AND COALESCE(usp.city_name, '') = COALESCE(p_city_name, '')
      AND COALESCE(usp.institution_name, '') = COALESCE(p_institution_name, '');

    IF NOT FOUND THEN
        INSERT INTO public.user_server_permissions (
            server_id, discord_id, permission_code, city_name, institution_name, granted, granted_by
        )
        VALUES (
            v_server_id, p_target_discord_id, p_permission_code, p_city_name, p_institution_name, TRUE, p_actor_discord_id
        );
    END IF;

    RETURN TRUE;
END;
$$;

-- RPC-like function: revoke permission with enforcement
-- Row-based allow model: revoke = DELETE row (permission disappears)
CREATE OR REPLACE FUNCTION public.revoke_user_permission(
    p_server_key TEXT,
    p_actor_discord_id TEXT,
    p_target_discord_id TEXT,
    p_permission_code TEXT,
    p_city_name TEXT DEFAULT NULL,
    p_institution_name TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_id UUID;
BEGIN
    SELECT id INTO v_server_id
    FROM public.app_servers
    WHERE server_key = p_server_key
    LIMIT 1;

    IF v_server_id IS NULL THEN
        RETURN FALSE;
    END IF;

    IF NOT public.can_actor_manage_target(v_server_id, p_actor_discord_id, p_target_discord_id, p_permission_code, 'revoke') THEN
        RETURN FALSE;
    END IF;

    DELETE FROM public.user_server_permissions usp
    WHERE usp.server_id = v_server_id
      AND usp.discord_id = p_target_discord_id
      AND usp.permission_code = p_permission_code
      AND COALESCE(usp.city_name, '') = COALESCE(p_city_name, '')
      AND COALESCE(usp.institution_name, '') = COALESCE(p_institution_name, '');

    RETURN TRUE;
END;
$$;

-- 10) City/Institution-first helpers (server kept implicit/technical)
-- Set a default server once, then manage permissions by city/institution only.
CREATE TABLE IF NOT EXISTS public.app_runtime_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.app_runtime_settings(key, value)
VALUES ('default_server_key', 'server_alpha')
ON CONFLICT (key) DO NOTHING;

CREATE OR REPLACE FUNCTION public.get_default_server_id()
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_key TEXT;
    v_server_id UUID;
BEGIN
    SELECT value INTO v_server_key
    FROM public.app_runtime_settings
    WHERE key = 'default_server_key'
    LIMIT 1;

    IF v_server_key IS NULL OR btrim(v_server_key) = '' THEN
        RETURN NULL;
    END IF;

    SELECT id INTO v_server_id
    FROM public.app_servers
    WHERE server_key = v_server_key
    LIMIT 1;

    RETURN v_server_id;
END;
$$;

-- Wrapper: grant WITHOUT passing server_key each time (city/institution-first usage)
CREATE OR REPLACE FUNCTION public.grant_user_permission_scoped(
    p_actor_discord_id TEXT,
    p_target_discord_id TEXT,
    p_permission_code TEXT,
    p_city_name TEXT DEFAULT NULL,
    p_institution_name TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_id UUID;
BEGIN
    v_server_id := public.get_default_server_id();
    IF v_server_id IS NULL THEN
        RETURN FALSE;
    END IF;

    IF NOT public.can_actor_manage_target(v_server_id, p_actor_discord_id, p_target_discord_id, p_permission_code, 'grant') THEN
        RETURN FALSE;
    END IF;

    UPDATE public.user_server_permissions usp
    SET granted = TRUE,
        granted_by = p_actor_discord_id,
        updated_at = NOW()
    WHERE usp.server_id = v_server_id
      AND usp.discord_id = p_target_discord_id
      AND usp.permission_code = p_permission_code
      AND COALESCE(usp.city_name, '') = COALESCE(p_city_name, '')
      AND COALESCE(usp.institution_name, '') = COALESCE(p_institution_name, '');

    IF NOT FOUND THEN
        INSERT INTO public.user_server_permissions (
            server_id, discord_id, permission_code, city_name, institution_name, granted, granted_by
        )
        VALUES (
            v_server_id, p_target_discord_id, p_permission_code, p_city_name, p_institution_name, TRUE, p_actor_discord_id
        );
    END IF;

    RETURN TRUE;
END;
$$;

-- Wrapper: revoke WITHOUT passing server_key each time (city/institution-first usage)
-- Row-based allow model: revoke = DELETE row (permission disappears)
CREATE OR REPLACE FUNCTION public.revoke_user_permission_scoped(
    p_actor_discord_id TEXT,
    p_target_discord_id TEXT,
    p_permission_code TEXT,
    p_city_name TEXT DEFAULT NULL,
    p_institution_name TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_id UUID;
BEGIN
    v_server_id := public.get_default_server_id();
    IF v_server_id IS NULL THEN
        RETURN FALSE;
    END IF;

    IF NOT public.can_actor_manage_target(v_server_id, p_actor_discord_id, p_target_discord_id, p_permission_code, 'revoke') THEN
        RETURN FALSE;
    END IF;

    DELETE FROM public.user_server_permissions usp
    WHERE usp.server_id = v_server_id
      AND usp.discord_id = p_target_discord_id
      AND usp.permission_code = p_permission_code
      AND COALESCE(usp.city_name, '') = COALESCE(p_city_name, '')
      AND COALESCE(usp.institution_name, '') = COALESCE(p_institution_name, '');

    RETURN TRUE;
END;
$$;

COMMIT;

-- =========================
-- EXAMPLES
-- =========================

-- IMPORTANT DEFAULT-DENY RULE (city/institution first):
-- Dacă NU există rând în user_server_permissions (allow row),
-- utilizatorul NU are acces (inclusiv la orașe noi adăugate pe viitor).
-- Pentru userii normali, NU acorda permisiuni globale (city_name/institution_name NULL)
-- pentru can_view/can_edit/can_delete, altfel vor primi acces și la orașele noi.

-- Cleanup opțional (o singură dată): elimină rândurile vechi cu granted = FALSE
-- DELETE FROM public.user_server_permissions WHERE granted = FALSE;

-- A) Add two servers
-- INSERT INTO public.app_servers(server_key, server_name)
-- VALUES ('server_alpha', 'Server Alpha'), ('server_beta', 'Server Beta')
-- ON CONFLICT (server_key) DO NOTHING;

-- A1) Grant owner/superuser rights (global) ONLY to your Discord ID on one server
-- INSERT INTO public.user_server_permissions(server_id, discord_id, permission_code, city_name, institution_name, granted, granted_by)
-- SELECT s.id, 'DISCORD_ID_AL_TAU', p.permission_code, NULL, NULL, TRUE, 'DISCORD_ID_AL_TAU'
-- FROM public.app_servers s
-- JOIN public.app_permissions p ON p.permission_code IN (
--   'can_manage_user_permissions','can_see_user_permissions_button','can_see_admin_panel','can_see_admin_button',
--   'can_add_cities','can_edit_cities','can_delete_cities','can_view_logs'
-- )
-- WHERE s.server_key = 'server_alpha';

-- A2) Add logged users from 44808 into a specific server membership (source table)
-- INSERT INTO public.server_users(server_id, discord_id, username_snapshot)
-- SELECT s.id, dlu.discord_id, dlu.username
-- FROM public.app_servers s
-- JOIN public.discord_login_users dlu ON TRUE
-- WHERE s.server_key = 'server_alpha'
-- ON CONFLICT (server_id, discord_id)
-- DO UPDATE SET username_snapshot = EXCLUDED.username_snapshot, updated_at = NOW();

-- B) Give BlackWater can_view ONLY on server_alpha
-- WITH srv AS (
--   SELECT id AS server_id FROM public.app_servers WHERE server_key = 'server_alpha' LIMIT 1
-- ), updated AS (
--   UPDATE public.user_server_permissions usp
--   SET granted = TRUE, granted_by = 'admin_discord_id', updated_at = NOW()
--   FROM srv
--   WHERE usp.server_id = srv.server_id
--     AND usp.discord_id = '123456789012345678'
--     AND usp.permission_code = 'can_view'
--     AND COALESCE(usp.city_name, '') = 'BlackWater'
--     AND COALESCE(usp.institution_name, '') = ''
--   RETURNING usp.id
-- )
-- INSERT INTO public.user_server_permissions(server_id, discord_id, permission_code, city_name, institution_name, granted, granted_by)
-- SELECT srv.server_id, '123456789012345678', 'can_view', 'BlackWater', NULL, TRUE, 'admin_discord_id'
-- FROM srv
-- WHERE NOT EXISTS (SELECT 1 FROM updated);

-- C) Verify isolation (should return only server_alpha permission)
-- SELECT server_key, discord_id, username, permission_code, city_name, granted
-- FROM public.v_user_server_permissions
-- WHERE discord_id = '123456789012345678' AND city_name = 'BlackWater'
-- ORDER BY server_key;

-- D) Mark you as superuser (protected from delegated edits)
-- INSERT INTO public.server_superusers(server_id, discord_id)
-- SELECT id, 'DISCORD_ID_AL_TAU'
-- FROM public.app_servers
-- WHERE server_key = 'server_alpha'
-- ON CONFLICT (server_id, discord_id) DO NOTHING;

-- E) Delegate user X to manage permissions (grant+revoke) on server_alpha
-- INSERT INTO public.permission_admin_delegations(server_id, granted_by_discord_id, manager_discord_id, can_grant, can_revoke, is_active)
-- SELECT s.id, 'DISCORD_ID_AL_TAU', 'DISCORD_ID_X', TRUE, TRUE, TRUE
-- FROM public.app_servers s
-- WHERE s.server_key = 'server_alpha'
-- ON CONFLICT (server_id, manager_discord_id)
-- DO UPDATE SET can_grant = EXCLUDED.can_grant, can_revoke = EXCLUDED.can_revoke, is_active = TRUE, updated_at = NOW();

-- F) City/Institution-first calls (no server_key in UI):
-- SELECT public.grant_user_permission_scoped('DISCORD_ID_X', 'DISCORD_ID_Y', 'can_view', 'BlackWater', NULL);
-- SELECT public.grant_user_permission_scoped('DISCORD_ID_X', 'DISCORD_ID_Y', 'can_add_employee', 'BlackWater', 'politie');
-- SELECT public.revoke_user_permission_scoped('DISCORD_ID_X', 'DISCORD_ID_Y', 'can_add_employee', 'BlackWater', 'politie');
-- SELECT public.grant_user_permission_scoped('DISCORD_ID_X', 'DISCORD_ID_AL_TAU', 'can_view', 'BlackWater', NULL); -- returns false for superuser target
