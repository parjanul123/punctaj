-- Adaugă coloana pentru acțiuni în tabela employees din Supabase
ALTER TABLE public.employees 
ADD COLUMN IF NOT EXISTS actiuni_detalii jsonb DEFAULT '[]'::jsonb;

-- Adaugă un comentariu pentru claritate
COMMENT ON COLUMN public.employees.actiuni_detalii IS 'JSON array containing detailed actions: [{"tip": "razie", "locatie": "Valentine", "data": "01.03.2026 15:30", "puncte": 5}]';

-- Creează un index pentru performanță la căutări în JSON
CREATE INDEX IF NOT EXISTS idx_employees_actiuni_detalii 
ON public.employees USING GIN (actiuni_detalii);

-- Test: Verifică că coloana s-a adăugat
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'employees' 
               AND column_name = 'actiuni_detalii') THEN
        RAISE NOTICE '✅ Coloana actiuni_detalii a fost adăugată cu succes!';
    ELSE
        RAISE EXCEPTION '❌ Coloana actiuni_detalii NU s-a adăugat!';
    END IF;
END $$;