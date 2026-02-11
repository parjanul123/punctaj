-- Tabelă pentru rapoartele săptămânale din arhiva
CREATE TABLE IF NOT EXISTS weekly_reports (
    id BIGSERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    city VARCHAR(255) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    employee_count INTEGER DEFAULT 0,
    reset_by VARCHAR(255),
    discord_id VARCHAR(50),
    report_data JSONB,
    archived_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabelă pentru detaliile angajaților din raportele săptămânale
CREATE TABLE IF NOT EXISTS weekly_report_details (
    id BIGSERIAL PRIMARY KEY,
    weekly_report_id BIGINT NOT NULL REFERENCES weekly_reports(id) ON DELETE CASCADE,
    employee_name VARCHAR(255) NOT NULL,
    employee_email VARCHAR(255),
    position VARCHAR(255),
    monday_hours DECIMAL(5,2) DEFAULT 0,
    tuesday_hours DECIMAL(5,2) DEFAULT 0,
    wednesday_hours DECIMAL(5,2) DEFAULT 0,
    thursday_hours DECIMAL(5,2) DEFAULT 0,
    friday_hours DECIMAL(5,2) DEFAULT 0,
    saturday_hours DECIMAL(5,2) DEFAULT 0,
    sunday_hours DECIMAL(5,2) DEFAULT 0,
    total_hours DECIMAL(6,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'present', -- present, absent, medical_leave, vacation, etc.
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pentru căutări rapide
CREATE INDEX IF NOT EXISTS idx_weekly_reports_week ON weekly_reports(week_start, week_end);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_city_inst ON weekly_reports(city, institution);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_created_at ON weekly_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_weekly_report_details_report_id ON weekly_report_details(weekly_report_id);
CREATE INDEX IF NOT EXISTS idx_weekly_report_details_employee ON weekly_report_details(employee_name);

-- View pentru rapoarte săptămânale detaliate
CREATE OR REPLACE VIEW weekly_report_view AS
SELECT 
    wr.id as report_id,
    wr.week_start,
    wr.week_end,
    wr.city,
    wr.institution,
    wrd.employee_name,
    wrd.position,
    wrd.monday_hours,
    wrd.tuesday_hours,
    wrd.wednesday_hours,
    wrd.thursday_hours,
    wrd.friday_hours,
    wrd.saturday_hours,
    wrd.sunday_hours,
    wrd.total_hours,
    wrd.status,
    wrd.notes,
    wr.created_at as report_created_at
FROM weekly_reports wr
LEFT JOIN weekly_report_details wrd ON wr.id = wrd.weekly_report_id
ORDER BY wr.week_start DESC, wr.institution, wrd.employee_name;

-- View pentru rapoarte lunare (agregate pe luni)
CREATE OR REPLACE VIEW monthly_reports AS
SELECT 
    DATE_TRUNC('month', wr.week_start)::DATE as month,
    wr.city,
    wr.institution,
    COUNT(DISTINCT wrd.id) as total_employee_records,
    COUNT(DISTINCT wr.id) as weekly_reports_count,
    SUM(wrd.total_hours) as total_hours_worked,
    MAX(wr.created_at) as last_report_date
FROM weekly_reports wr
LEFT JOIN weekly_report_details wrd ON wr.id = wrd.weekly_report_id
GROUP BY DATE_TRUNC('month', wr.week_start), wr.city, wr.institution
ORDER BY month DESC, wr.city, wr.institution;

-- Trigger pentru update_at (weekly_reports)
CREATE OR REPLACE FUNCTION update_weekly_reports_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_weekly_reports_timestamp ON weekly_reports;
CREATE TRIGGER trigger_update_weekly_reports_timestamp
BEFORE UPDATE ON weekly_reports
FOR EACH ROW
EXECUTE FUNCTION update_weekly_reports_timestamp();

-- Trigger pentru update_at (weekly_report_details)
CREATE OR REPLACE FUNCTION update_weekly_report_details_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_weekly_report_details_timestamp ON weekly_report_details;
CREATE TRIGGER trigger_update_weekly_report_details_timestamp
BEFORE UPDATE ON weekly_report_details
FOR EACH ROW
EXECUTE FUNCTION update_weekly_report_details_timestamp();

-- Trigger pentru actualizare automată a total_hours
CREATE OR REPLACE FUNCTION calculate_total_hours()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_hours = COALESCE(NEW.monday_hours, 0) + 
                      COALESCE(NEW.tuesday_hours, 0) + 
                      COALESCE(NEW.wednesday_hours, 0) + 
                      COALESCE(NEW.thursday_hours, 0) + 
                      COALESCE(NEW.friday_hours, 0) + 
                      COALESCE(NEW.saturday_hours, 0) + 
                      COALESCE(NEW.sunday_hours, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calculate_total_hours ON weekly_report_details;
CREATE TRIGGER trigger_calculate_total_hours
BEFORE INSERT OR UPDATE ON weekly_report_details
FOR EACH ROW
EXECUTE FUNCTION calculate_total_hours();
