-- Tabelă pentru tracking versiunilor și sincronizare cloud
CREATE TABLE IF NOT EXISTS sync_metadata (
    id BIGSERIAL PRIMARY KEY,
    sync_key VARCHAR(255) UNIQUE NOT NULL,  -- e.g., 'global_version', 'city:{city_id}', 'institution:{inst_id}'
    version BIGINT DEFAULT 1,
    last_modified_by VARCHAR(255),
    last_modified_at TIMESTAMP DEFAULT NOW(),
    data_hash VARCHAR(64),  -- SHA256 hash pentru detectare schimbări
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pentru căutări rapide
CREATE INDEX IF NOT EXISTS idx_sync_metadata_key ON sync_metadata(sync_key);
CREATE INDEX IF NOT EXISTS idx_sync_metadata_updated ON sync_metadata(updated_at);

-- Trigger pentru update_at
CREATE OR REPLACE FUNCTION update_sync_metadata_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_sync_metadata_timestamp ON sync_metadata;
CREATE TRIGGER trigger_update_sync_metadata_timestamp
BEFORE UPDATE ON sync_metadata
FOR EACH ROW
EXECUTE FUNCTION update_sync_metadata_timestamp();

-- Inițializează versiunea globală
INSERT INTO sync_metadata (sync_key, version, last_modified_by, data_hash)
VALUES ('global_version', 1, 'system', NULL)
ON CONFLICT (sync_key) DO NOTHING;

-- Tabelă pentru tracking sincronizări
CREATE TABLE IF NOT EXISTS sync_log (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    discord_id VARCHAR(50),
    sync_type VARCHAR(50),  -- 'upload', 'download', 'force_sync'
    status VARCHAR(50),  -- 'pending', 'in_progress', 'success', 'failed'
    items_synced INTEGER DEFAULT 0,
    error_message TEXT,
    synced_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pentru căutări rapide
CREATE INDEX IF NOT EXISTS idx_sync_log_user ON sync_log(discord_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);
CREATE INDEX IF NOT EXISTS idx_sync_log_created ON sync_log(created_at);
