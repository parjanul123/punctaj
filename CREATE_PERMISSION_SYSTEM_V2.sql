-- Permission system (normalized) for Discord users
-- Run in Supabase SQL Editor

BEGIN;

-- 1) Catalog de permisiuni (lista funcțiilor din aplicație)
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

-- 2) Tabela de asociere user -> permisiune
-- Folosește discord_id ca foreign key logic către discord_login_users.discord_id
CREATE TABLE IF NOT EXISTS public.user_app_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id TEXT NOT NULL,
    permission_code TEXT NOT NULL,
    granted BOOLEAN NOT NULL DEFAULT TRUE,
    granted_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_permission UNIQUE (discord_id, permission_code),
    CONSTRAINT fk_permission_code
        FOREIGN KEY (permission_code)
        REFERENCES public.app_permissions(permission_code)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 3) Index-uri pentru performanță
CREATE INDEX IF NOT EXISTS idx_uap_discord_id ON public.user_app_permissions(discord_id);
CREATE INDEX IF NOT EXISTS idx_uap_permission_code ON public.user_app_permissions(permission_code);
CREATE INDEX IF NOT EXISTS idx_uap_granted ON public.user_app_permissions(granted);

-- 4) Trigger pentru updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_app_permissions_updated_at ON public.app_permissions;
CREATE TRIGGER trg_app_permissions_updated_at
BEFORE UPDATE ON public.app_permissions
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_user_app_permissions_updated_at ON public.user_app_permissions;
CREATE TRIGGER trg_user_app_permissions_updated_at
BEFORE UPDATE ON public.user_app_permissions
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 5) Seed permisiuni (ajustează după ce folosește exact aplicația ta)
INSERT INTO public.app_permissions (permission_code, display_name, category, description)
VALUES
('can_view', 'Vizualizare date', 'core', 'Acces vizualizare date aplicație'),
('can_edit', 'Editare date', 'core', 'Poate modifica date'),
('can_delete', 'Ștergere date', 'core', 'Poate șterge date'),
('can_edit_employee', 'Editare angajați', 'employees', 'Poate edita angajați'),
('can_delete_employee', 'Ștergere angajați', 'employees', 'Poate șterge angajați'),
('can_add_cities', 'Adăugare orașe', 'admin', 'Poate adăuga orașe'),
('can_edit_cities', 'Editare orașe', 'admin', 'Poate edita orașe'),
('can_delete_cities', 'Ștergere orașe', 'admin', 'Poate șterge orașe'),
('can_view_logs', 'Vizualizare loguri', 'logs', 'Poate vedea loguri'),
('can_see_admin_panel', 'Panou admin', 'ui', 'Poate vedea panoul admin'),
('can_see_user_permissions_button', 'Buton permisiuni utilizatori', 'ui', 'Poate vedea butonul de permisiuni utilizatori'),
('can_see_admin_button', 'Buton admin', 'ui', 'Poate vedea butonul admin')
ON CONFLICT (permission_code) DO NOTHING;

-- 6) View util: toți userii + permisiunile active
CREATE OR REPLACE VIEW public.v_user_permissions AS
SELECT
    u.discord_id,
    u.username,
    p.permission_code,
    p.display_name,
    COALESCE(up.granted, FALSE) AS granted,
    up.updated_at AS granted_updated_at
FROM public.discord_login_users u
CROSS JOIN public.app_permissions p
LEFT JOIN public.user_app_permissions up
       ON up.discord_id = u.discord_id
      AND up.permission_code = p.permission_code
WHERE p.is_active = TRUE;

COMMIT;

-- Exemple utile:
-- 1) Acordă o permisiune unui user
-- INSERT INTO public.user_app_permissions (discord_id, permission_code, granted, granted_by)
-- VALUES ('123456789012345678', 'can_view', TRUE, 'admin_discord_id')
-- ON CONFLICT (discord_id, permission_code)
-- DO UPDATE SET granted = EXCLUDED.granted, granted_by = EXCLUDED.granted_by, updated_at = NOW();

-- 2) Toți userii care au acces la o funcție
-- SELECT discord_id, username
-- FROM public.v_user_permissions
-- WHERE permission_code = 'can_view' AND granted = TRUE
-- ORDER BY username;
