-- Station Service Database Schema
-- SQLite database schema for local storage

-- Station 설정 (변경 이력용)
CREATE TABLE IF NOT EXISTS station_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 실행 결과
CREATE TABLE IF NOT EXISTS execution_results (
    id TEXT PRIMARY KEY,              -- "exec_20250120_123456"
    batch_id TEXT NOT NULL,
    sequence_name TEXT NOT NULL,
    sequence_version TEXT NOT NULL,
    status TEXT NOT NULL,             -- running, completed, failed, stopped
    overall_pass BOOLEAN,
    parameters_json TEXT,             -- JSON
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    duration INTEGER,                 -- seconds
    synced_at DATETIME,               -- Backend 동기화 시간
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 실행 결과 인덱스
CREATE INDEX IF NOT EXISTS idx_execution_results_batch_id ON execution_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_execution_results_status ON execution_results(status);
CREATE INDEX IF NOT EXISTS idx_execution_results_started_at ON execution_results(started_at);

-- Step 결과
CREATE TABLE IF NOT EXISTS step_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    status TEXT NOT NULL,             -- pending, running, completed, failed, skipped
    pass BOOLEAN,
    result_json TEXT,                 -- JSON
    error TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    duration REAL,                    -- seconds (float)
    FOREIGN KEY (execution_id) REFERENCES execution_results(id) ON DELETE CASCADE
);

-- Step 결과 인덱스
CREATE INDEX IF NOT EXISTS idx_step_results_execution_id ON step_results(execution_id);

-- 로그
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    execution_id TEXT,
    level TEXT NOT NULL,              -- debug, info, warning, error
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 로그 인덱스
CREATE INDEX IF NOT EXISTS idx_logs_batch_id ON logs(batch_id);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);

-- 동기화 큐 (오프라인 모드)
CREATE TABLE IF NOT EXISTS sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,        -- execution, log
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,             -- create, update
    payload_json TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 동기화 큐 인덱스
CREATE INDEX IF NOT EXISTS idx_sync_queue_entity_type ON sync_queue(entity_type);
