-- =============================================================================
-- DDL Script: processes (제조 공정)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Master data table defining the 8 manufacturing processes
-- Dependencies: None (independent table)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS processes CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE processes (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Core columns
    process_number INTEGER NOT NULL,           -- Process sequence number (1-8)
    process_code VARCHAR(50) NOT NULL,         -- Unique process code (e.g., LASER_MARKING)
    process_name_ko VARCHAR(255) NOT NULL,     -- Process name in Korean
    process_name_en VARCHAR(255) NOT NULL,     -- Process name in English
    description TEXT,                          -- Process description and details
    estimated_duration_seconds INTEGER,        -- Expected duration in seconds
    quality_criteria JSONB DEFAULT '{}',       -- Quality standards and acceptance criteria
    is_active BOOLEAN NOT NULL DEFAULT TRUE,   -- Whether process is currently in use
    sort_order INTEGER NOT NULL,               -- Display order (usually same as process_number)

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE processes
ADD CONSTRAINT pk_processes PRIMARY KEY (id);

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================
ALTER TABLE processes
ADD CONSTRAINT uk_processes_process_number UNIQUE (process_number);

ALTER TABLE processes
ADD CONSTRAINT uk_processes_process_code UNIQUE (process_code);

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Process number must be between 1 and 8
ALTER TABLE processes
ADD CONSTRAINT chk_processes_process_number
CHECK (process_number >= 1 AND process_number <= 8);

-- Duration must be positive if specified
ALTER TABLE processes
ADD CONSTRAINT chk_processes_duration
CHECK (estimated_duration_seconds IS NULL OR estimated_duration_seconds > 0);

-- Sort order must be positive
ALTER TABLE processes
ADD CONSTRAINT chk_processes_sort_order
CHECK (sort_order > 0);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Active processes index
CREATE INDEX idx_processes_active
ON processes(is_active, sort_order)
WHERE is_active = TRUE;

-- GIN index for JSONB quality_criteria
CREATE INDEX idx_processes_quality_criteria
ON processes USING gin(quality_criteria);

-- Sort order for UI display
CREATE INDEX idx_processes_sort_order
ON processes(sort_order);

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_processes_updated_at
BEFORE UPDATE ON processes
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_processes_audit
AFTER INSERT OR UPDATE OR DELETE ON processes
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- Prevent deletion if process data exists
CREATE TRIGGER trg_processes_prevent_delete
BEFORE DELETE ON processes
FOR EACH ROW
EXECUTE FUNCTION prevent_process_deletion();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE processes IS 'Master data table defining the 8 manufacturing processes in the F2X production line';
COMMENT ON COLUMN processes.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN processes.process_number IS 'Process sequence number (1-8)';
COMMENT ON COLUMN processes.process_code IS 'Unique process code (e.g., LASER_MARKING)';
COMMENT ON COLUMN processes.process_name_ko IS 'Process name in Korean';
COMMENT ON COLUMN processes.process_name_en IS 'Process name in English';
COMMENT ON COLUMN processes.description IS 'Process description and details';
COMMENT ON COLUMN processes.estimated_duration_seconds IS 'Expected duration in seconds';
COMMENT ON COLUMN processes.quality_criteria IS 'Quality standards and acceptance criteria in JSONB format';
COMMENT ON COLUMN processes.is_active IS 'Whether process is currently in use';
COMMENT ON COLUMN processes.sort_order IS 'Display order (usually same as process_number)';
COMMENT ON COLUMN processes.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN processes.updated_at IS 'Last update timestamp';

-- =============================================================================
-- INITIAL DATA - 8 MANUFACTURING PROCESSES (REQUIRED)
-- =============================================================================
INSERT INTO processes (process_number, process_code, process_name_ko, process_name_en, estimated_duration_seconds, quality_criteria, sort_order) VALUES
-- Process 1: Laser Marking
(1, 'LASER_MARKING', '레이저 마킹', 'Laser Marking', 60,
 '{
    "power": "20W",
    "speed": "100mm/s",
    "depth": "0.1mm",
    "marking_quality": "GOOD",
    "readability_threshold": 0.95,
    "position_tolerance_mm": 0.1
  }', 1),

-- Process 2: LMA Assembly
(2, 'LMA_ASSEMBLY', 'LMA 조립', 'LMA Assembly', 180,
 '{
    "components_required": ["LMA_module", "connector", "screws"],
    "torque_spec": {"min": 0.8, "max": 1.2, "unit": "Nm"},
    "alignment_tolerance_mm": 0.1,
    "visual_check": true,
    "assembly_duration_seconds": 180,
    "acceptance_criteria": "All components properly assembled and aligned"
  }', 2),

-- Process 3: Sensor Inspection
(3, 'SENSOR_INSPECTION', '센서 검사', 'Sensor Inspection', 120,
 '{
    "sensor_channels": 8,
    "signal_quality_threshold": 0.85,
    "noise_level_max_db": -40,
    "calibration_required": true,
    "test_patterns": ["baseline", "stimulus", "recovery"],
    "acceptance_criteria": "All channels functional with signal quality >0.85"
  }', 3),

-- Process 4: Firmware Upload
(4, 'FIRMWARE_UPLOAD', '펌웨어 업로드', 'Firmware Upload', 300,
 '{
    "firmware_version": "2.1.0",
    "checksum_validation": true,
    "upload_protocol": "UART",
    "baud_rate": 115200,
    "verification_required": true,
    "retry_attempts": 3,
    "acceptance_criteria": "Firmware uploaded and verified successfully"
  }', 4),

-- Process 5: Robot Assembly
(5, 'ROBOT_ASSEMBLY', '로봇 조립', 'Robot Assembly', 300,
 '{
    "robot_components": ["motor", "encoder", "gear_assembly"],
    "motor_test": {
      "rotation_speed_rpm": 1000,
      "current_draw_ma": 500,
      "torque_nm": 2.5
    },
    "encoder_resolution": 4096,
    "functional_test_required": true,
    "assembly_duration_seconds": 300,
    "acceptance_criteria": "Full mechanical and electrical functionality verified"
  }', 5),

-- Process 6: Performance Test
(6, 'PERFORMANCE_TEST', '성능검사', 'Performance Test', 180,
 '{
    "response_time_ms": 50,
    "accuracy_percent": 95,
    "throughput_samples_per_sec": 1000,
    "test_scenarios": ["idle", "load", "stress"],
    "stability_test_duration_seconds": 120,
    "acceptance_criteria": "All performance metrics within specifications"
  }', 6),

-- Process 7: Label Printing
(7, 'LABEL_PRINTING', '라벨 프린팅', 'Label Printing', 30,
 '{
    "label_type": "barcode",
    "resolution": "300dpi",
    "verification_required": true,
    "print_quality_check": true,
    "barcode_readability": 0.99,
    "label_alignment_tolerance_mm": 1.0,
    "acceptance_criteria": "Label printed clearly and verified readable"
  }', 7),

-- Process 8: Packaging & Visual Inspection
(8, 'PACKAGING_INSPECTION', '포장 + 외관검사', 'Packaging & Visual Inspection', 90,
 '{
    "anti_static_bag": true,
    "visual_defect_check": true,
    "label_verification": true,
    "packaging_materials": ["anti_static_bag", "cushioning", "outer_box"],
    "inspection_points": ["scratches", "dents", "color_uniformity", "label_placement"],
    "documentation_included": true,
    "acceptance_criteria": "No visual defects and properly packaged"
  }', 8);

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================