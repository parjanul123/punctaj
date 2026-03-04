-- ===============================================
-- SETUP COMPLET BAZA DE DATE PENTRU RAPORT ACȚIUNI
-- ===============================================
-- Acest fișier conține toate operațiunile necesare pentru:
-- 1. Adăugarea coloanei actiuni_detalii la tabela employees
-- 2. Crearea tabelei employees_tipuri_actiuni pentru raport
-- 3. Funcții și triggere pentru sincronizare automată
-- ===============================================

-- PASUL 1: Adău coloana actiuni_detalii la tabela employees (dacă nu există)
-- ===============================================

DO $$
BEGIN
    -- Verifică dacă coloana există deja
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'actiuni_detalii'
    ) THEN
        -- Adaugă coloana pentru stocarea acțiunilor ca JSON
        ALTER TABLE employees 
        ADD COLUMN actiuni_detalii JSONB DEFAULT '[]'::jsonb;
        
        RAISE NOTICE 'Coloana actiuni_detalii a fost adăugată cu succes!';
    ELSE
        RAISE NOTICE 'Coloana actiuni_detalii există deja.';
    END IF;
END
$$;

-- ===============================================
-- PASUL 2: Creează tabela pentru raportul de activități
-- ===============================================

-- Șterge tabela dacă există pentru a o recrea
DROP TABLE IF EXISTS employees_tipuri_actiuni CASCADE;

-- Creează tabela pentru raportul de activități
CREATE TABLE employees_tipuri_actiuni (
    id SERIAL PRIMARY KEY,
    employee_id TEXT,
    employee_name TEXT NOT NULL,
    institutie_id INTEGER,
    razie INTEGER DEFAULT 0,
    patrula_oras INTEGER DEFAULT 0,
    filtru INTEGER DEFAULT 0,
    patrula_nocturna INTEGER DEFAULT 0,
    total_actiuni INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pentru performanță
CREATE INDEX IF NOT EXISTS idx_employees_tipuri_actiuni_employee_id ON employees_tipuri_actiuni(employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_tipuri_actiuni_institutie_id ON employees_tipuri_actiuni(institutie_id);CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_tipuri_actiuni_unique_employee ON employees_tipuri_actiuni(employee_id);
COMMENT ON TABLE employees_tipuri_actiuni IS 'Tabela pentru raportul de activități - conține numărul de acțiuni pe tipuri pentru fiecare angajat';

-- ===============================================
-- PASUL 3: Funcția pentru recalcularea automată a acțiunilor
-- ===============================================

CREATE OR REPLACE FUNCTION recalc_employee_actiuni()
RETURNS TRIGGER AS $$
BEGIN
    -- Șterge înregistrarea veche dacă există
    DELETE FROM employees_tipuri_actiuni WHERE employee_id = NEW.id::text;
    
    -- Calculează acțiunile din coloana actiuni_detalii
    DECLARE
        razie_count INTEGER := 0;
        patrula_oras_count INTEGER := 0;
        filtru_count INTEGER := 0;
        patrula_nocturna_count INTEGER := 0;
        total_count INTEGER := 0;
        actiune JSONB;
        tip_actiune TEXT;
    BEGIN
        -- Procesează fiecare acțiune din JSON
        IF NEW.actiuni_detalii IS NOT NULL THEN
            FOR actiune IN SELECT jsonb_array_elements(NEW.actiuni_detalii)
            LOOP
                tip_actiune := actiune->>'tip';
                
                CASE tip_actiune
                    WHEN 'razie' THEN razie_count := razie_count + 1;
                    WHEN 'patrula_oras' THEN patrula_oras_count := patrula_oras_count + 1;
                    WHEN 'filtru' THEN filtru_count := filtru_count + 1;
                    WHEN 'patrula_nocturna' THEN patrula_nocturna_count := patrula_nocturna_count + 1;
                END CASE;
            END LOOP;
        END IF;
        
        total_count := razie_count + patrula_oras_count + filtru_count + patrula_nocturna_count;
        
        -- Inserează sau actualizează înregistrarea
        INSERT INTO employees_tipuri_actiuni (
            employee_id,
            employee_name,
            institutie_id,
            razie,
            patrula_oras,
            filtru,
            patrula_nocturna,
            total_actiuni,
            last_updated
        ) VALUES (
            NEW.id::text,
            COALESCE(NULLIF(NEW.employee_name, ''), NEW.discord_username, 'Unknown'),
            NEW.institution_id,
            razie_count,
            patrula_oras_count,
            filtru_count,
            patrula_nocturna_count,
            total_count,
            NOW()
        );
        
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ===============================================
-- PASUL 4: Triggere pentru actualizare automată
-- ===============================================

-- Trigger pentru INSERT (angajați noi)
DROP TRIGGER IF EXISTS trigger_employee_actiuni_insert ON employees;
CREATE TRIGGER trigger_employee_actiuni_insert
    AFTER INSERT ON employees
    FOR EACH ROW
    EXECUTE FUNCTION recalc_employee_actiuni();

-- Trigger pentru UPDATE (modificări la acțiuni)
DROP TRIGGER IF EXISTS trigger_employee_actiuni_update ON employees;
CREATE TRIGGER trigger_employee_actiuni_update
    AFTER UPDATE OF actiuni_detalii ON employees
    FOR EACH ROW
    EXECUTE FUNCTION recalc_employee_actiuni();

-- ===============================================
-- PASUL 5: Populează tabela cu datele existente
-- ===============================================

-- Populează tabela cu toți angajații existenți
INSERT INTO employees_tipuri_actiuni (
    employee_id,
    employee_name,
    institutie_id,
    razie,
    patrula_oras,
    filtru,
    patrula_nocturna,
    total_actiuni,
    last_updated
)
SELECT 
    e.id::text as employee_id,
    COALESCE(NULLIF(e.employee_name, ''), e.discord_username, 'Unknown') as employee_name,
    e.institution_id,
    COALESCE(
        (SELECT COUNT(*) 
         FROM jsonb_array_elements(COALESCE(e.actiuni_detalii, '[]'::jsonb)) AS actiune 
         WHERE actiune->>'tip' = 'razie'), 0
    ) as razie,
    COALESCE(
        (SELECT COUNT(*) 
         FROM jsonb_array_elements(COALESCE(e.actiuni_detalii, '[]'::jsonb)) AS actiune 
         WHERE actiune->>'tip' = 'patrula_oras'), 0
    ) as patrula_oras,
    COALESCE(
        (SELECT COUNT(*) 
         FROM jsonb_array_elements(COALESCE(e.actiuni_detalii, '[]'::jsonb)) AS actiune 
         WHERE actiune->>'tip' = 'filtru'), 0
    ) as filtru,
    COALESCE(
        (SELECT COUNT(*) 
         FROM jsonb_array_elements(COALESCE(e.actiuni_detalii, '[]'::jsonb)) AS actiune 
         WHERE actiune->>'tip' = 'patrula_nocturna'), 0
    ) as patrula_nocturna,
    COALESCE(jsonb_array_length(COALESCE(e.actiuni_detalii, '[]'::jsonb)), 0) as total_actiuni,
    NOW() as last_updated
FROM employees e
ON CONFLICT (employee_id) DO UPDATE SET
    employee_name = EXCLUDED.employee_name,
    institution_id = EXCLUDED.institution_id,
    razie = EXCLUDED.razie,
    patrula_oras = EXCLUDED.patrula_oras,
    filtru = EXCLUDED.filtru,
    patrula_nocturna = EXCLUDED.patrula_nocturna,
    total_actiuni = EXCLUDED.total_actiuni,
    last_updated = NOW();

-- ===============================================
-- PASUL 6: Testare și verificare
-- ===============================================

-- Afișează statistici finale
DO $$
DECLARE
    emp_count INTEGER;
    raport_count INTEGER;
    total_actiuni INTEGER;
BEGIN
    SELECT COUNT(*) INTO emp_count FROM employees;
    SELECT COUNT(*) INTO raport_count FROM employees_tipuri_actiuni;
    SELECT SUM(total_actiuni) INTO total_actiuni FROM employees_tipuri_actiuni;
    
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'SETUP COMPLET FINALIZAT CU SUCCES!';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Angajați în tabela employees: %', emp_count;
    RAISE NOTICE 'Înregistrări în raportul de activități: %', raport_count;
    RAISE NOTICE 'Total acțiuni înregistrate: %', COALESCE(total_actiuni, 0);
    RAISE NOTICE '==========================================';
END
$$;

-- Verifică dacă totul funcționează
SELECT 
    'Setup verification' as test_name,
    COUNT(*) as employees_count,
    (SELECT COUNT(*) FROM employees_tipuri_actiuni) as report_count,
    (SELECT SUM(total_actiuni) FROM employees_tipuri_actiuni) as total_actions
FROM employees;

-- ===============================================
-- GATA! 
-- ===============================================
-- Acum poți folosi:
-- 1. Coloana actiuni_detalii din tabela employees pentru JSON-ul cu acțiuni
-- 2. Tabela employees_tipuri_actiuni pentru raportul de activități
-- 3. Triggerele vor actualiza automat raportul când se modifică acțiunile
-- ===============================================