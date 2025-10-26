-- ParallelDev Database Schema
-- SQLite Database for Project Management and Tracking
-- Created: 2025-10-25

-- ============================================================================
-- Projects Table
-- Stores information about each discovered project
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    parent_id INTEGER,
    description TEXT,
    requirements_content TEXT,
    todo_content TEXT,
    readme_content TEXT,
    status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed', 'blocked')) DEFAULT 'not_started',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Index for parent-child relationships
CREATE INDEX IF NOT EXISTS idx_projects_parent_id ON projects(parent_id);

-- Index for path lookups
CREATE INDEX IF NOT EXISTS idx_projects_path ON projects(path);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- ============================================================================
-- Requirements Table
-- Stores parsed requirements from REQUIREMENTS.md files
-- ============================================================================
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    category TEXT,
    description TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('critical', 'high', 'medium', 'low', 'unknown')) DEFAULT 'unknown',
    status TEXT CHECK(status IN ('planned', 'in_progress', 'completed', 'blocked')) DEFAULT 'planned',
    requirement_number INTEGER,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Index for project-based queries
CREATE INDEX IF NOT EXISTS idx_requirements_project_id ON requirements(project_id);

-- Index for priority filtering
CREATE INDEX IF NOT EXISTS idx_requirements_priority ON requirements(priority);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_requirements_status ON requirements(status);

-- ============================================================================
-- Tasks Table
-- Stores parsed tasks from TODO.md files
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    section TEXT,
    stage TEXT,
    description TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('critical', 'high', 'medium', 'low', 'unknown')) DEFAULT 'unknown',
    status TEXT CHECK(status IN ('todo', 'in_progress', 'done', 'blocked')) DEFAULT 'todo',
    order_number INTEGER,
    line_number INTEGER,
    parent_task_id INTEGER,
    estimated_effort TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Index for project-based queries
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- Index for priority filtering
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Index for hierarchical queries
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks(parent_task_id);

-- ============================================================================
-- Metrics Table
-- Stores calculated metrics and historical data
-- ============================================================================
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    metric_type TEXT NOT NULL CHECK(metric_type IN (
        'completion_percentage',
        'task_count_total',
        'task_count_completed',
        'task_count_in_progress',
        'task_count_not_started',
        'requirement_count_total',
        'requirement_count_implemented',
        'requirement_coverage',
        'velocity',
        'estimated_completion_days'
    )),
    value REAL NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Index for project-based queries
CREATE INDEX IF NOT EXISTS idx_metrics_project_id ON metrics(project_id);

-- Index for metric type filtering
CREATE INDEX IF NOT EXISTS idx_metrics_metric_type ON metrics(metric_type);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_metrics_calculated_at ON metrics(calculated_at);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_metrics_project_type_date ON metrics(project_id, metric_type, calculated_at);

-- ============================================================================
-- Scan History Table
-- Tracks when scans were performed and their results
-- ============================================================================
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_completed_at TIMESTAMP,
    projects_scanned INTEGER DEFAULT 0,
    projects_added INTEGER DEFAULT 0,
    projects_updated INTEGER DEFAULT 0,
    projects_removed INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    scan_duration_seconds REAL,
    status TEXT CHECK(status IN ('running', 'completed', 'failed')) DEFAULT 'running',
    error_message TEXT
);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_scan_history_started_at ON scan_history(scan_started_at);

-- ============================================================================
-- File Changes Table
-- Tracks detected file changes for monitoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS file_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    file_path TEXT NOT NULL,
    change_type TEXT CHECK(change_type IN ('created', 'modified', 'deleted')) NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Index for project-based queries
CREATE INDEX IF NOT EXISTS idx_file_changes_project_id ON file_changes(project_id);

-- Index for processing status
CREATE INDEX IF NOT EXISTS idx_file_changes_processed ON file_changes(processed);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_file_changes_detected_at ON file_changes(detected_at);

-- ============================================================================
-- AI Agent Sessions Table (Future Use)
-- Tracks AI agent activities and results
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_agent_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    task_id INTEGER,
    agent_type TEXT,
    provider TEXT CHECK(provider IN ('claude', 'openai', 'openrouter')),
    model TEXT,
    session_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('running', 'completed', 'failed', 'cancelled')) DEFAULT 'running',
    prompt TEXT,
    response TEXT,
    tokens_used INTEGER,
    cost REAL,
    error_message TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Index for project-based queries
CREATE INDEX IF NOT EXISTS idx_ai_sessions_project_id ON ai_agent_sessions(project_id);

-- Index for task-based queries
CREATE INDEX IF NOT EXISTS idx_ai_sessions_task_id ON ai_agent_sessions(task_id);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_ai_sessions_started_at ON ai_agent_sessions(session_started_at);

-- ============================================================================
-- Configuration Table
-- Stores runtime configuration that can be modified
-- ============================================================================
CREATE TABLE IF NOT EXISTS configuration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration values
INSERT OR IGNORE INTO configuration (key, value, description) VALUES
    ('scan_interval_seconds', '300', 'Interval between automatic scans'),
    ('file_watch_enabled', 'true', 'Enable real-time file monitoring'),
    ('metrics_history_days', '90', 'Days to retain metrics history'),
    ('ai_enabled', 'false', 'Enable AI integration features');

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- Project Summary View
-- Provides aggregated statistics for each project
CREATE VIEW IF NOT EXISTS vw_project_summary AS
SELECT 
    p.id,
    p.name,
    p.path,
    p.status,
    p.last_scanned,
    COUNT(DISTINCT t.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as completed_tasks,
    COUNT(DISTINCT CASE WHEN t.status = 'in_progress' THEN t.id END) as in_progress_tasks,
    COUNT(DISTINCT CASE WHEN t.status = 'todo' THEN t.id END) as not_started_tasks,
    COUNT(DISTINCT r.id) as total_requirements,
    COUNT(DISTINCT CASE WHEN r.status = 'completed' THEN r.id END) as implemented_requirements,
    CASE
        WHEN COUNT(DISTINCT t.id) > 0
        THEN CAST(COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) AS REAL) / COUNT(DISTINCT t.id) * 100
        ELSE 0
    END as completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
LEFT JOIN requirements r ON p.id = r.project_id
GROUP BY p.id, p.name, p.path, p.status, p.last_scanned;

-- Recent Metrics View
-- Shows the most recent metric value for each project and metric type
CREATE VIEW IF NOT EXISTS vw_recent_metrics AS
SELECT 
    m1.project_id,
    m1.metric_type,
    m1.value,
    m1.calculated_at
FROM metrics m1
INNER JOIN (
    SELECT project_id, metric_type, MAX(calculated_at) as max_date
    FROM metrics
    GROUP BY project_id, metric_type
) m2 ON m1.project_id = m2.project_id
    AND m1.metric_type = m2.metric_type
    AND m1.calculated_at = m2.max_date;

-- ============================================================================
-- Triggers for Automatic Timestamp Updates
-- ============================================================================

-- Update last_modified timestamp on projects table
CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
AFTER UPDATE ON projects
FOR EACH ROW
BEGIN
    UPDATE projects SET last_modified = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update updated_at timestamp on requirements table
CREATE TRIGGER IF NOT EXISTS update_requirements_timestamp 
AFTER UPDATE ON requirements
FOR EACH ROW
BEGIN
    UPDATE requirements SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update updated_at timestamp on tasks table
CREATE TRIGGER IF NOT EXISTS update_tasks_timestamp 
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Set completed_at timestamp when task is marked complete
CREATE TRIGGER IF NOT EXISTS set_task_completed_timestamp
AFTER UPDATE OF status ON tasks
FOR EACH ROW
WHEN NEW.status = 'done' AND OLD.status != 'done'
BEGIN
    UPDATE tasks SET completed_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update configuration timestamp
CREATE TRIGGER IF NOT EXISTS update_configuration_timestamp 
AFTER UPDATE ON configuration
FOR EACH ROW
BEGIN
    UPDATE configuration SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- Database Version and Metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) VALUES
    (1, 'Initial schema creation with core tables and indexes');
