-- 1) Tabela raport (se actualizează automat de trigger)
CREATE TABLE IF NOT EXISTS public.employees_tipuri_actiuni (
  employee_id bigint PRIMARY KEY REFERENCES public.employees(id) ON DELETE CASCADE,
  institution_id bigint,
  employee_name text,
  razie integer NOT NULL DEFAULT 0,
  patrula_oras integer NOT NULL DEFAULT 0,
  filtru integer NOT NULL DEFAULT 0,
  patrula_nocturna integer NOT NULL DEFAULT 0,
  total_actiuni integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Index pentru performanță
CREATE INDEX IF NOT EXISTS idx_employees_tipuri_institutie 
ON public.employees_tipuri_actiuni(institution_id);

-- 2) Funcție: recalculează pentru un employee (CORECTATĂ să lucreze cu ACTIUNI_DETALII)
CREATE OR REPLACE FUNCTION public.recalc_employee_actiuni(p_employee_id bigint)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_razie integer := 0;
  v_patrula_oras integer := 0;
  v_filtru integer := 0;
  v_patrula_nocturna integer := 0;
  v_employee_name text;
  v_institution_id bigint;
  v_actiuni_json jsonb;
  v_actiune jsonb;
BEGIN
  -- Preiau datele employee-ului și JSON-ul cu acțiunile
  SELECT employee_name, institution_id, COALESCE(actiuni_detalii, '[]'::jsonb)
  INTO v_employee_name, v_institution_id, v_actiuni_json
  FROM public.employees
  WHERE id = p_employee_id;

  -- Parcurg JSON-ul și contabilizez acțiunile pe tip
  FOR v_actiune IN SELECT * FROM jsonb_array_elements(v_actiuni_json)
  LOOP
    CASE v_actiune->>'tip'
      WHEN 'Razie' THEN
        v_razie := v_razie + 1;
      WHEN 'Patrula oras' THEN
        v_patrula_oras := v_patrula_oras + 1;
      WHEN 'Filtru' THEN
        v_filtru := v_filtru + 1;
      WHEN 'Patrula nocturna' THEN
        v_patrula_nocturna := v_patrula_nocturna + 1;
    END CASE;
  END LOOP;

  -- Insert sau Update în raport
  INSERT INTO public.employees_tipuri_actiuni 
  (employee_id, institution_id, employee_name, razie, patrula_oras, filtru, patrula_nocturna, total_actiuni, updated_at)
  VALUES 
  (p_employee_id, v_institution_id, v_employee_name, v_razie, v_patrula_oras, v_filtru, v_patrula_nocturna, 
   v_razie + v_patrula_oras + v_filtru + v_patrula_nocturna, now())
  ON CONFLICT (employee_id) DO UPDATE SET
    razie = v_razie,
    patrula_oras = v_patrula_oras,
    filtru = v_filtru,
    patrula_nocturna = v_patrula_nocturna,
    total_actiuni = v_razie + v_patrula_oras + v_filtru + v_patrula_nocturna,
    updated_at = now();
END;
$$;

-- 3) Trigger: când se adaugă/modifică/șterge în employees (ACTIUNI_DETALII)
CREATE OR REPLACE FUNCTION public.trg_employees_actiuni_recalc()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    PERFORM public.recalc_employee_actiuni(NEW.id);
  
  ELSIF TG_OP = 'DELETE' THEN
    PERFORM public.recalc_employee_actiuni(OLD.id);
  
  ELSIF TG_OP = 'UPDATE' THEN
    -- Doar dacă s-a modificat actiuni_detalii
    IF OLD.actiuni_detalii IS DISTINCT FROM NEW.actiuni_detalii THEN
      PERFORM public.recalc_employee_actiuni(NEW.id);
    END IF;
  END IF;
  
  RETURN COALESCE(NEW, OLD);
END;
$$;

-- Șterge trigger-ul vechi dacă există și creează cel nou
DROP TRIGGER IF EXISTS trg_employees_after_iud ON public.employees;
CREATE TRIGGER trg_employees_after_iud
AFTER INSERT OR UPDATE OR DELETE ON public.employees
FOR EACH ROW
EXECUTE FUNCTION public.trg_employees_actiuni_recalc();

-- 4) Backfill: populează pentru toți employees existenți
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT id FROM public.employees LOOP
    PERFORM public.recalc_employee_actiuni(r.id);
  END LOOP;
END $$;