-- =============================================================================
-- F2X NeuroHub MES - Test Data Script
-- =============================================================================
-- Purpose: Load sample data for testing and demonstration
-- Usage: psql -U postgres -d f2x_neurohub_mes -f test_data.sql
-- Or: docker exec -it f2x-postgres psql -U postgres -d f2x_neurohub_mes -f /sql/test_data.sql
-- =============================================================================

\set ON_ERROR_STOP on
\timing on

\echo ''
\echo '============================================================================='
\echo 'Loading Test Data for F2X NeuroHub MES'
\echo '============================================================================='
\echo ''

BEGIN;

-- =============================================================================
-- 1. Product Models
-- =============================================================================
\echo '📦 Step 1/5: Inserting Product Models...'

INSERT INTO product_models (model_code, model_name, version, specifications, status)
VALUES
    (
        'PSA-1000',
        'NeuroHub PSA 1000',
        '1.0',
        '{
            "voltage": "12V",
            "current": "5A",
            "power": "60W",
            "dimensions": {"width": 100, "height": 50, "depth": 150},
            "weight": 500,
            "certifications": ["CE", "FCC", "RoHS"]
        }'::jsonb,
        'ACTIVE'
    ),
    (
        'PSA-2000',
        'NeuroHub PSA 2000',
        '2.0',
        '{
            "voltage": "24V",
            "current": "10A",
            "power": "240W",
            "dimensions": {"width": 150, "height": 75, "depth": 200},
            "weight": 800,
            "certifications": ["CE", "FCC", "RoHS", "UL"]
        }'::jsonb,
        'ACTIVE'
    ),
    (
        'PSA-3000',
        'NeuroHub PSA 3000 (Beta)',
        '3.0-beta',
        '{
            "voltage": "48V",
            "current": "20A",
            "power": "960W",
            "dimensions": {"width": 200, "height": 100, "depth": 250},
            "weight": 1200,
            "certifications": ["CE", "FCC"],
            "notes": "Beta version - under development"
        }'::jsonb,
        'DEVELOPMENT'
    )
ON CONFLICT (model_code) DO NOTHING;

\echo '   ✅ Product models inserted'

-- =============================================================================
-- 2. LOTs (Production Batches)
-- =============================================================================
\echo '📋 Step 2/5: Inserting LOTs...'

-- LOT 1: Completed today (DAY shift)
INSERT INTO lots (product_model_id, target_quantity, shift, production_date, status)
VALUES (
    (SELECT id FROM product_models WHERE model_code = 'PSA-1000'),
    50,
    'DAY',
    CURRENT_DATE,
    'IN_PROGRESS'
);

-- LOT 2: Completed today (NIGHT shift)
INSERT INTO lots (product_model_id, target_quantity, shift, production_date, status)
VALUES (
    (SELECT id FROM product_models WHERE model_code = 'PSA-1000'),
    30,
    'NIGHT',
    CURRENT_DATE,
    'IN_PROGRESS'
);

-- LOT 3: Yesterday (DAY shift) - Completed
INSERT INTO lots (product_model_id, target_quantity, shift, production_date, status)
VALUES (
    (SELECT id FROM product_models WHERE model_code = 'PSA-2000'),
    20,
    'DAY',
    CURRENT_DATE - INTERVAL '1 day',
    'COMPLETED'
);

-- LOT 4: 2 days ago (NIGHT shift) - Closed
INSERT INTO lots (product_model_id, target_quantity, shift, production_date, status, closed_at)
VALUES (
    (SELECT id FROM product_models WHERE model_code = 'PSA-2000'),
    25,
    'NIGHT',
    CURRENT_DATE - INTERVAL '2 days',
    'CLOSED',
    CURRENT_TIMESTAMP - INTERVAL '1 day'
);

-- LOT 5: Beta product (DAY shift) - Just created
INSERT INTO lots (product_model_id, target_quantity, shift, production_date, status)
VALUES (
    (SELECT id FROM product_models WHERE model_code = 'PSA-3000'),
    5,
    'DAY',
    CURRENT_DATE,
    'CREATED'
);

\echo '   ✅ LOTs inserted (LOT numbers auto-generated)'

-- =============================================================================
-- 3. Serials (Individual Units)
-- =============================================================================
\echo '🔢 Step 3/5: Inserting Serials...'

-- Helper function to insert serials for a LOT
DO $$
DECLARE
    lot_record RECORD;
    serial_count INTEGER;
BEGIN
    -- For each LOT, create serials
    FOR lot_record IN SELECT id, target_quantity, status FROM lots LOOP
        serial_count := 0;

        -- Determine how many serials to create based on LOT status
        IF lot_record.status = 'CREATED' THEN
            serial_count := 0;  -- No serials yet
        ELSIF lot_record.status = 'IN_PROGRESS' THEN
            serial_count := LEAST(lot_record.target_quantity / 2, 10);  -- Half of target, max 10
        ELSIF lot_record.status IN ('COMPLETED', 'CLOSED') THEN
            serial_count := LEAST(lot_record.target_quantity, 10);  -- Full target, max 10
        END IF;

        -- Insert serials
        FOR i IN 1..serial_count LOOP
            INSERT INTO serials (lot_id, status)
            VALUES (
                lot_record.id,
                CASE
                    WHEN lot_record.status = 'CLOSED' THEN 'PASSED'
                    WHEN i <= serial_count / 2 THEN 'IN_PROGRESS'
                    ELSE 'CREATED'
                END
            );
        END LOOP;
    END LOOP;
END $$;

\echo '   ✅ Serials inserted (Serial numbers auto-generated)'

-- =============================================================================
-- 4. Process Data (Manufacturing Records)
-- =============================================================================
\echo '⚙️  Step 4/5: Inserting Process Data...'

-- Insert process data for completed serials
DO $$
DECLARE
    serial_record RECORD;
    process_record RECORD;
    operator_id INTEGER;
BEGIN
    -- Get operator user ID
    SELECT id INTO operator_id FROM users WHERE username = 'operator1';

    -- For each PASSED serial, create complete process history
    FOR serial_record IN
        SELECT s.id AS serial_id, s.lot_id, s.serial_number
        FROM serials s
        WHERE s.status = 'PASSED'
    LOOP
        -- Create process data for all 8 processes
        FOR process_record IN
            SELECT id, process_number, process_code, expected_duration_seconds
            FROM processes
            ORDER BY process_number
        LOOP
            INSERT INTO process_data (
                lot_id,
                serial_id,
                process_id,
                operator_id,
                started_at,
                ended_at,
                result,
                measurements
            )
            VALUES (
                serial_record.lot_id,
                serial_record.serial_id,
                process_record.id,
                operator_id,
                CURRENT_TIMESTAMP - (8 - process_record.process_number) * INTERVAL '1 hour',
                CURRENT_TIMESTAMP - (8 - process_record.process_number) * INTERVAL '1 hour'
                    + (process_record.expected_duration_seconds || ' seconds')::INTERVAL,
                'PASS',
                jsonb_build_object(
                    'temperature', 25.0 + random() * 5.0,
                    'humidity', 45.0 + random() * 10.0,
                    'quality_score', 90 + random() * 10
                )
            );
        END LOOP;
    END LOOP;

    -- For IN_PROGRESS serials, create partial process history
    FOR serial_record IN
        SELECT s.id AS serial_id, s.lot_id, s.serial_number
        FROM serials s
        WHERE s.status = 'IN_PROGRESS'
        LIMIT 5
    LOOP
        -- Create process data for first 4 processes only
        FOR process_record IN
            SELECT id, process_number, process_code, expected_duration_seconds
            FROM processes
            WHERE process_number <= 4
            ORDER BY process_number
        LOOP
            INSERT INTO process_data (
                lot_id,
                serial_id,
                process_id,
                operator_id,
                started_at,
                ended_at,
                result,
                measurements
            )
            VALUES (
                serial_record.lot_id,
                serial_record.serial_id,
                process_record.id,
                operator_id,
                CURRENT_TIMESTAMP - (4 - process_record.process_number) * INTERVAL '30 minutes',
                CURRENT_TIMESTAMP - (4 - process_record.process_number) * INTERVAL '30 minutes'
                    + (process_record.expected_duration_seconds || ' seconds')::INTERVAL,
                CASE
                    WHEN random() < 0.9 THEN 'PASS'
                    ELSE 'FAIL'
                END,
                jsonb_build_object(
                    'temperature', 25.0 + random() * 5.0,
                    'humidity', 45.0 + random() * 10.0,
                    'quality_score', 85 + random() * 15
                )
            );
        END LOOP;
    END LOOP;

    -- Add some FAILED records for testing
    FOR serial_record IN
        SELECT s.id AS serial_id, s.lot_id
        FROM serials s
        WHERE s.status = 'IN_PROGRESS'
        LIMIT 2
    LOOP
        -- Add a failed process
        INSERT INTO process_data (
            lot_id,
            serial_id,
            process_id,
            operator_id,
            started_at,
            ended_at,
            result,
            defects,
            measurements
        )
        VALUES (
            serial_record.lot_id,
            serial_record.serial_id,
            (SELECT id FROM processes WHERE process_code = 'SENSOR_INSPECTION'),
            operator_id,
            CURRENT_TIMESTAMP - INTERVAL '1 hour',
            CURRENT_TIMESTAMP - INTERVAL '59 minutes',
            'FAIL',
            jsonb_build_array(
                jsonb_build_object(
                    'defect_code', 'SENSOR_001',
                    'defect_name', 'Sensor reading out of range',
                    'severity', 'HIGH',
                    'description', 'Sensor reading: 105% (expected: 95-100%)'
                )
            ),
            jsonb_build_object(
                'temperature', 28.5,
                'humidity', 52.0,
                'sensor_reading', 105.2,
                'quality_score', 65
            )
        );
    END LOOP;
END $$;

\echo '   ✅ Process data inserted'

-- =============================================================================
-- 5. Summary Statistics
-- =============================================================================
\echo ''
\echo '📊 Step 5/5: Test Data Summary'
\echo ''

-- Product Models
SELECT
    'Product Models' AS category,
    COUNT(*) AS count,
    STRING_AGG(model_code, ', ' ORDER BY model_code) AS items
FROM product_models;

-- LOTs by Status
SELECT
    'LOTs by Status' AS category,
    status,
    COUNT(*) AS count,
    STRING_AGG(lot_number, ', ' ORDER BY lot_number) AS lot_numbers
FROM lots
GROUP BY status
ORDER BY status;

-- Serials by Status
SELECT
    'Serials by Status' AS category,
    status,
    COUNT(*) AS count
FROM serials
GROUP BY status
ORDER BY status;

-- Process Data Summary
SELECT
    'Process Data' AS category,
    result,
    COUNT(*) AS count
FROM process_data
GROUP BY result
ORDER BY result;

-- Overall Statistics
SELECT
    'Overall Statistics' AS metric,
    jsonb_pretty(jsonb_build_object(
        'product_models', (SELECT COUNT(*) FROM product_models),
        'lots', (SELECT COUNT(*) FROM lots),
        'serials', (SELECT COUNT(*) FROM serials),
        'process_records', (SELECT COUNT(*) FROM process_data),
        'users', (SELECT COUNT(*) FROM users),
        'processes', (SELECT COUNT(*) FROM processes)
    )) AS statistics;

COMMIT;

\echo ''
\echo '============================================================================='
\echo '✅ Test Data Loaded Successfully!'
\echo '============================================================================='
\echo ''
\echo '📝 Sample Queries to Try:'
\echo ''
\echo '1. View all LOTs:'
\echo '   SELECT lot_number, status, target_quantity, actual_quantity FROM lots;'
\echo ''
\echo '2. View serials with their LOT:'
\echo '   SELECT l.lot_number, s.serial_number, s.status FROM serials s JOIN lots l ON s.lot_id = l.id;'
\echo ''
\echo '3. View process completion rate:'
\echo '   SELECT p.process_name_en, COUNT(*) as total, SUM(CASE WHEN pd.result = '\''PASS'\'' THEN 1 ELSE 0 END) as passed'
\echo '   FROM process_data pd JOIN processes p ON pd.process_id = p.id GROUP BY p.id, p.process_name_en;'
\echo ''
\echo '4. View recent audit logs:'
\echo '   SELECT entity_type, action, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 10;'
\echo ''
\echo '============================================================================='
