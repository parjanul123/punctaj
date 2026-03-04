-- ===============================================
-- SETUP SIMPLU BAZA DE DATE PUNCTAJ
-- ===============================================
-- Fișier actualizat fără tipurile de acțiuni
-- (Înlocuiește SETUP_COMPLETE_DATABASE.sql)
-- ===============================================

-- ===============================================
-- PASUL 1: Verifică și curăță structura veche
-- ===============================================

-- Elimină sistemul vechi cu tipuri acțiuni dacă există
DROP TABLE IF EXISTS employees_tipuri_actiuni CASCADE;
DROP TRIGGER IF EXISTS trigger_employee_actiuni_insert ON employees;
DROP TRIGGER IF EXISTS trigger_employee_actiuni_update ON employees;
DROP FUNCTION IF EXISTS recalc_employee_actiuni() CASCADE;

-- Elimină coloana actiuni_detalii dacă există
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'actiuni_detalii'
    ) THEN
        ALTER TABLE employees DROP COLUMN actiuni_detalii;
        RAISE NOTICE 'Coloana actiuni_detalii eliminată cu succes';
    ELSE
        RAISE NOTICE 'Coloana actiuni_detalii nu există - skip';
    END IF;
END $$;

-- ===============================================
-- PASUL 2: Asigură structura simplă pentru employees
-- ===============================================

-- Verifică și actualizează structura tabelei employees
DO $$
BEGIN
    -- Asigură că avem coloanele necesare pentru punctajul simplu
    
    -- Verifică și adaugă coloana punctaj dacă nu există
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'punctaj'
    ) THEN
        ALTER TABLE employees ADD COLUMN punctaj INTEGER DEFAULT 0;
        RAISE NOTICE 'Coloana punctaj adăugată cu succes';
    END IF;
    
    -- Verifică și adaugă coloana nr_actiuni dacă nu există (numărul simplu de acțiuni)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'nr_actiuni'
    ) THEN
        ALTER TABLE employees ADD COLUMN nr_actiuni INTEGER DEFAULT 0;
        RAISE NOTICE 'Coloana nr_actiuni adăugată cu succes';
    END IF;
    
    -- Verifică și adaugă coloana zona dacă nu există (locația opțională)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'zona'
    ) THEN
        ALTER TABLE employees ADD COLUMN zona TEXT;
        RAISE NOTICE 'Coloana zona adăugată cu succes';
    END IF;
    
    -- Verifică și adaugă coloana ultima_modificare dacă nu există
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'ultima_modificare'
    ) THEN
        ALTER TABLE employees ADD COLUMN ultima_modificare TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Coloana ultima_modificare adăugată cu succes';
    END IF;
    
    RAISE NOTICE 'Structura simplă pentru punctaj verificată și actualizată';
END $$;

-- ===============================================
-- PASUL 3: Indexuri pentru performanță
-- ===============================================

-- Index pentru punctaj (pentru sortare rapidă)
CREATE INDEX IF NOT EXISTS idx_employees_punctaj ON employees(punctaj DESC);

-- Index pentru zona (pentru filtrare rapidă)
CREATE INDEX IF NOT EXISTS idx_employees_zona ON employees(zona);

-- Index pentru nr_actiuni (pentru statistici)
CREATE INDEX IF NOT EXISTS idx_employees_nr_actiuni ON employees(nr_actiuni DESC);

-- Index pentru ultima_modificare (pentru audit)
CREATE INDEX IF NOT EXISTS idx_employees_ultima_modificare ON employees(ultima_modificare DESC);

-- ===============================================
-- PASUL 4: Trigger pentru actualizarea automată a ultima_modificare
-- ===============================================

-- Funcție pentru actualizarea automată a timpului de modificare
CREATE OR REPLACE FUNCTION update_employee_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizează timpul doar dacă punctajul, nr_actiuni sau zona s-au modificat
    IF OLD.punctaj IS DISTINCT FROM NEW.punctaj 
       OR OLD.nr_actiuni IS DISTINCT FROM NEW.nr_actiuni
       OR OLD.zona IS DISTINCT FROM NEW.zona THEN
        NEW.ultima_modificare := NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pentru UPDATE
DROP TRIGGER IF EXISTS trigger_employee_timestamp_update ON employees;
CREATE TRIGGER trigger_employee_timestamp_update
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_employee_timestamp();

-- ===============================================
-- PASUL 5: Verificare și statistici finale
-- ===============================================

DO $$
DECLARE
    emp_count INTEGER;
    total_punctaj INTEGER;
    total_actiuni INTEGER;
    avg_punctaj NUMERIC;
BEGIN
    SELECT COUNT(*) INTO emp_count FROM employees;
    SELECT SUM(COALESCE(punctaj, 0)) INTO total_punctaj FROM employees;
    SELECT SUM(COALESCE(nr_actiuni, 0)) INTO total_actiuni FROM employees;
    SELECT ROUND(AVG(COALESCE(punctaj, 0)), 2) INTO avg_punctaj FROM employees WHERE punctaj > 0;
    
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'SETUP SIMPLU FINALIZAT CU SUCCES!';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Total angajați: %', emp_count;
    RAISE NOTICE 'Total punctaj sistem: %', COALESCE(total_punctaj, 0);
    RAISE NOTICE 'Total acțiuni sistem: %', COALESCE(total_actiuni, 0);
    RAISE NOTICE 'Punctaj mediu: %', COALESCE(avg_punctaj, 0);
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'SISTEM SIMPLIFICAT:';
    RAISE NOTICE '- Punctaj simplu (număr)';
    RAISE NOTICE '- Număr acțiuni (fără categorisire)';
    RAISE NOTICE '- Zona opțională (locație)';
    RAISE NOTICE '- Fără tipuri de acțiuni complexe';
    RAISE NOTICE '==========================================';
END
$$;

-- Verificare finală - afișează structura curățată
SELECT 
    'Database verification' as test_name,
    COUNT(*) as employees_count,
    SUM(COALESCE(punctaj, 0)) as total_points,
    SUM(COALESCE(nr_actiuni, 0)) as total_actions,
    COUNT(DISTINCT zona) as unique_zones
FROM employees;

-- ===============================================
-- GATA! SISTEM SIMPLIFICAT
-- ===============================================
-- Acum sistemul folosește:
-- 1. employees.punctaj - punctajul simplu (INTEGER)
-- 2. employees.nr_actiuni - numărul de acțiuni (INTEGER) 
-- 3. employees.zona - locația opțională (TEXT)
-- 4. employees.ultima_modificare - timestamp automat
-- 
-- ELIMINAT complet:
-- - Tabela employees_tipuri_actiuni
-- - Coloana actiuni_detalii JSONB
-- - Tipurile de acțiuni (razie, patrulă, filtru, etc.)
-- - Justificările complexe
-- ===============================================

COMMENT ON TABLE employees IS 'Tabela angajaților cu sistem simplificat de punctaj - fără tipuri de acțiuni';
COMMENT ON COLUMN employees.punctaj IS 'Punctajul simplu numeric al angajatului';
COMMENT ON COLUMN employees.nr_actiuni IS 'Numărul total de acțiuni fără categorisire';
COMMENT ON COLUMN employees.zona IS 'Zona/locația opțională pentru ultima acțiune';
COMMENT ON COLUMN employees.ultima_modificare IS 'Timestamp automat pentru ultima modificare de punctaj/acțiuni';