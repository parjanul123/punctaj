-- ===============================================
-- CLEANUP RAPORT ACȚIUNI - ELIMINARE COMPLETĂ
-- ===============================================
-- Acest fișier elimină complet funcționalitatea de raport acțiuni:
-- 1. Șterge triggere și funcții
-- 2. Șterge tabela employees_tipuri_actiuni
-- 3. Elimină coloana actiuni_detalii din tabela employees
-- ===============================================

-- PASUL 1: Eliminare triggere
-- ===============================================

DROP TRIGGER IF EXISTS trigger_employee_actiuni_insert ON employees;
DROP TRIGGER IF EXISTS trigger_employee_actiuni_update ON employees;

RAISE NOTICE 'Triggere eliminate cu succes!';

-- ===============================================
-- PASUL 2: Eliminare funcții
-- ===============================================

DROP FUNCTION IF EXISTS recalc_employee_actiuni();

RAISE NOTICE 'Funcții eliminate cu succes!';

-- ===============================================
-- PASUL 3: Eliminare tabela employees_tipuri_actiuni
-- ===============================================

DROP TABLE IF EXISTS employees_tipuri_actiuni CASCADE;

RAISE NOTICE 'Tabela employees_tipuri_actiuni eliminată cu succes!';

-- ===============================================
-- PASUL 4: Eliminare coloana actiuni_detalii din employees
-- ===============================================

DO $$
BEGIN
    -- Verifică dacă coloana există și o elimină
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'actiuni_detalii'
    ) THEN
        ALTER TABLE employees 
        DROP COLUMN actiuni_detalii;
        
        RAISE NOTICE 'Coloana actiuni_detalii a fost eliminată cu succes!';
    ELSE
        RAISE NOTICE 'Coloana actiuni_detalii nu există.';
    END IF;
END
$$;

-- ===============================================
-- PASUL 5: Verificare finală
-- ===============================================

DO $$
DECLARE
    emp_count INTEGER;
    column_exists BOOLEAN := FALSE;
    table_exists BOOLEAN := FALSE;
BEGIN
    SELECT COUNT(*) INTO emp_count FROM employees;
    
    -- Verifică dacă coloana mai există
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name = 'actiuni_detalii'
    ) INTO column_exists;
    
    -- Verifică dacă tabela mai există
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'employees_tipuri_actiuni'
    ) INTO table_exists;
    
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'CLEANUP COMPLET FINALIZAT CU SUCCES!';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Angajați rămași în tabela employees: %', emp_count;
    RAISE NOTICE 'Coloana actiuni_detalii eliminată: %', CASE WHEN NOT column_exists THEN 'DA' ELSE 'NU' END;
    RAISE NOTICE 'Tabela employees_tipuri_actiuni eliminată: %', CASE WHEN NOT table_exists THEN 'DA' ELSE 'NU' END;
    RAISE NOTICE '==========================================';
END
$$;

-- ===============================================
-- GATA! 
-- ===============================================
-- Funcționalitatea de raport acțiuni a fost eliminată complet!
-- Acum poți elimina și codul Python asociat.
-- 
-- ⚠️  NOTĂ IMPORTANTĂ:
-- - SETUP_COMPLETE_DATABASE.sql este acum OBSOLET
-- - Pentru setup nou, folosește SETUP_SIMPLE_DATABASE.sql
-- - Sistemul folosește acum punctaj simplu fără tipuri acțiuni
-- ===============================================