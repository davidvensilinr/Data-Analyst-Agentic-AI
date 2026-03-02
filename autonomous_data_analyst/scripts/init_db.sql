-- Database initialization script for PostgreSQL
-- This script sets up the database schema and initial data

-- Create database if it doesn't exist
-- (This is typically handled by the Docker entrypoint)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by SQLAlchemy but we can add additional ones

-- Index for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_run_id ON audit_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);

-- Index for runs
CREATE INDEX IF NOT EXISTS idx_runs_user_id ON runs(user_id);
CREATE INDEX IF NOT EXISTS idx_runs_dataset_id ON runs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at);

-- Index for run steps
CREATE INDEX IF NOT EXISTS idx_run_steps_run_id ON run_steps(run_id);
CREATE INDEX IF NOT EXISTS idx_run_steps_status ON run_steps(status);

-- Index for datasets
CREATE INDEX IF NOT EXISTS idx_datasets_owner_id ON datasets(owner_id);
CREATE INDEX IF NOT EXISTS idx_datasets_is_public ON datasets(is_public);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON datasets(created_at);

-- Index for API keys
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);

-- Create a default admin user (password: admin123)
-- In production, this should be handled more securely
INSERT INTO users (id, email, hashed_password, is_active, created_at)
VALUES (
    uuid_generate_v4(),
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkOYxjQw0mNb9k0f3J9QGqQJ5QJ5QJ5Q',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Create sample API key for admin user
INSERT INTO api_keys (id, key_hash, name, user_id, permissions, is_active, created_at)
VALUES (
    uuid_generate_v4(),
    '$2b$12$LQv3c1yqBWVHxkd0LHAkOYxjQw0mNb9k0f3J9QGqQJ5QJ5QJ5Q',
    'Default Admin Key',
    (SELECT id FROM users WHERE email = 'admin@example.com' LIMIT 1),
    '["*"]',
    true,
    NOW()
) ON CONFLICT DO NOTHING;

-- Set up database configuration
ALTER DATABASE postgres SET timezone = 'UTC';

-- Create view for active runs
CREATE OR REPLACE VIEW active_runs AS
SELECT 
    r.id,
    r.question,
    r.status,
    r.created_at,
    r.started_at,
    u.email as user_email,
    d.name as dataset_name
FROM runs r
JOIN users u ON r.user_id = u.id
JOIN datasets d ON r.dataset_id = d.id
WHERE r.status IN ('pending', 'running');

-- Create view for recent audit logs
CREATE OR REPLACE VIEW recent_audit_logs AS
SELECT 
    al.id,
    al.run_id,
    al.event_type,
    al.timestamp,
    u.email as user_email,
    al.data
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY al.timestamp DESC;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analyst_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analyst_user;
