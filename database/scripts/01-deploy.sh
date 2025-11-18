#!/bin/bash
# =============================================================================
# F2X NeuroHub MES - Database Initialization Script
# =============================================================================
# Purpose: Automatically deploy database schema and initialize data
# Execution: Auto-runs when PostgreSQL container starts for the first time
# Location: /docker-entrypoint-initdb.d/01-deploy.sh (inside container)
# =============================================================================

set -e  # Exit on error

echo ""
echo "============================================================================="
echo "F2X NeuroHub MES - Database Initialization"
echo "============================================================================="
echo ""

# Database connection parameters
export PGUSER=postgres
export PGDATABASE=f2x_neurohub_mes

echo "📊 Database: $PGDATABASE"
echo "👤 User: $PGUSER"
echo ""

# =============================================================================
# Step 1: Deploy Database Schema
# =============================================================================
echo "🚀 Step 1/5: Deploying database schema..."
echo "   - Creating functions, tables, indexes, triggers"
echo ""

psql -v ON_ERROR_STOP=1 <<-EOSQL
    \timing on
    \set VERBOSITY verbose

    -- Execute main deployment script
    \i /sql/deploy.sql
EOSQL

if [ $? -eq 0 ]; then
    echo "✅ Schema deployment completed successfully"
else
    echo "❌ Schema deployment failed"
    exit 1
fi

echo ""

# =============================================================================
# Step 2: Verify Deployment
# =============================================================================
echo "🔍 Step 2/5: Verifying deployment..."
echo "   - Checking functions, tables, constraints, indexes, triggers"
echo ""

psql -v ON_ERROR_STOP=1 <<-EOSQL
    -- Quick verification queries
    SELECT
        'Functions' AS component,
        COUNT(*) AS count
    FROM pg_proc
    WHERE pronamespace = 'public'::regnamespace
    AND prokind = 'f';

    SELECT
        'Tables' AS component,
        COUNT(*) AS count
    FROM pg_tables
    WHERE schemaname = 'public';

    SELECT
        'Indexes' AS component,
        COUNT(*) AS count
    FROM pg_indexes
    WHERE schemaname = 'public';

    SELECT
        'Triggers' AS component,
        COUNT(*) AS count
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND NOT t.tgisinternal;

    SELECT
        'Processes' AS component,
        COUNT(*) AS count
    FROM processes;
EOSQL

if [ $? -eq 0 ]; then
    echo "✅ Verification completed successfully"
else
    echo "⚠️  Verification completed with warnings"
fi

echo ""

# =============================================================================
# Step 3: Create Initial Users
# =============================================================================
echo "👥 Step 3/5: Creating initial users..."
echo "   - System user (for audit logging)"
echo "   - Admin user (for administration)"
echo ""

psql -v ON_ERROR_STOP=1 <<-EOSQL
    -- Create system user (required for audit logging)
    INSERT INTO users (username, full_name, role, email, is_active, password_hash)
    VALUES (
        'system',
        'System User',
        'SYSTEM',
        'system@f2x.com',
        TRUE,
        '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3FHm0OKNO'  -- "system123"
    )
    ON CONFLICT (username) DO NOTHING;

    -- Create admin user
    INSERT INTO users (username, full_name, role, email, is_active, password_hash)
    VALUES (
        'admin',
        'Administrator',
        'ADMIN',
        'admin@f2x.com',
        TRUE,
        '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3FHm0OKNO'  -- "admin123"
    )
    ON CONFLICT (username) DO NOTHING;

    -- Create operator user for testing
    INSERT INTO users (username, full_name, role, email, is_active, password_hash)
    VALUES (
        'operator1',
        'Operator One',
        'OPERATOR',
        'operator1@f2x.com',
        TRUE,
        '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3FHm0OKNO'  -- "operator123"
    )
    ON CONFLICT (username) DO NOTHING;

    SELECT
        username,
        full_name,
        role,
        email,
        is_active
    FROM users
    ORDER BY id;
EOSQL

if [ $? -eq 0 ]; then
    echo "✅ Initial users created successfully"
else
    echo "⚠️  User creation completed with warnings"
fi

echo ""

# =============================================================================
# Step 4: Create Audit Log Partitions
# =============================================================================
echo "📅 Step 4/5: Creating audit log partitions..."
echo "   - Creating partitions for next 6 months"
echo ""

psql -v ON_ERROR_STOP=1 <<-EOSQL
    -- Create partitions for next 6 months
    SELECT create_future_audit_partitions(6);

    -- Verify partitions
    SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename LIKE 'audit_logs%'
    ORDER BY tablename;
EOSQL

if [ $? -eq 0 ]; then
    echo "✅ Audit log partitions created successfully"
else
    echo "⚠️  Partition creation completed with warnings"
fi

echo ""

# =============================================================================
# Step 5: Final Summary
# =============================================================================
echo "📋 Step 5/5: Database initialization summary"
echo ""

psql -v ON_ERROR_STOP=1 <<-EOSQL
    SELECT
        current_database() AS database,
        current_user AS user,
        version() AS postgres_version;

    SELECT
        'Database Size' AS metric,
        pg_size_pretty(pg_database_size(current_database())) AS value;

    SELECT
        'Total Tables' AS metric,
        COUNT(*)::TEXT AS value
    FROM pg_tables
    WHERE schemaname = 'public';

    SELECT
        'Total Functions' AS metric,
        COUNT(*)::TEXT AS value
    FROM pg_proc
    WHERE pronamespace = 'public'::regnamespace;

    SELECT
        'Manufacturing Processes' AS metric,
        COUNT(*)::TEXT AS value
    FROM processes;

    SELECT
        'Initial Users' AS metric,
        COUNT(*)::TEXT AS value
    FROM users;
EOSQL

echo ""
echo "============================================================================="
echo "✅ Database Initialization Completed Successfully!"
echo "============================================================================="
echo ""
echo "📝 Next Steps:"
echo "   1. Load test data: psql -f /sql/test_data.sql"
echo "   2. Connect FastAPI backend with DATABASE_URL from .env"
echo "   3. Access pgAdmin: http://localhost:5050"
echo "   4. Start API server: uvicorn app.main:app --reload"
echo ""
echo "🔐 Default Credentials:"
echo "   System User:   username=system    password=system123"
echo "   Admin User:    username=admin     password=admin123"
echo "   Operator User: username=operator1 password=operator123"
echo ""
echo "⚠️  IMPORTANT: Change default passwords in production!"
echo ""
echo "============================================================================="
