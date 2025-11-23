#!/bin/bash

###############################################################################
# Migration Testing Script for F2X NeuroHub
#
# This script runs comprehensive migration tests including:
# - Forward migration testing
# - Rollback testing
# - Data integrity verification
# - Performance benchmarks
#
# Usage:
#   ./run_migration_tests.sh [options]
#
# Options:
#   -v, --verbose      Enable verbose output
#   -p, --performance  Run performance tests
#   -c, --coverage     Generate coverage report
#   -h, --help        Show this help message
#
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VERBOSE=0
RUN_PERFORMANCE=0
RUN_COVERAGE=0
TEST_DB_NAME="f2x_neurohub_migration_test"
BACKUP_DIR="./migration_backups"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -p|--performance)
            RUN_PERFORMANCE=1
            shift
            ;;
        -c|--coverage)
            RUN_COVERAGE=1
            shift
            ;;
        -h|--help)
            grep "^#" "$0" | grep -E "^# " | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print step headers
print_step() {
    echo ""
    print_message "$BLUE" "=========================================="
    print_message "$BLUE" "$1"
    print_message "$BLUE" "=========================================="
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking Prerequisites"

    # Check Python
    if ! command -v python &> /dev/null; then
        print_message "$RED" "Error: Python is not installed"
        exit 1
    fi

    # Check pytest
    if ! python -m pytest --version &> /dev/null; then
        print_message "$RED" "Error: pytest is not installed"
        echo "Install with: pip install pytest pytest-cov"
        exit 1
    fi

    # Check Alembic
    if ! python -m alembic --version &> /dev/null; then
        print_message "$RED" "Error: Alembic is not installed"
        echo "Install with: pip install alembic"
        exit 1
    fi

    # Check PostgreSQL connection (optional, for PostgreSQL testing)
    if command -v psql &> /dev/null; then
        print_message "$GREEN" "PostgreSQL client found"
    else
        print_message "$YELLOW" "Warning: PostgreSQL client not found, will use SQLite for testing"
    fi

    print_message "$GREEN" "All prerequisites met"
}

# Function to setup test database
setup_test_database() {
    print_step "Setting Up Test Database"

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Check if using PostgreSQL or SQLite
    if command -v psql &> /dev/null && [ -n "$DATABASE_URL" ]; then
        # PostgreSQL setup
        print_message "$YELLOW" "Setting up PostgreSQL test database..."

        # Parse DATABASE_URL to get connection details
        DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:\/]*\).*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

        # Create test database
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" 2>/dev/null || true
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $TEST_DB_NAME;"

        export TEST_DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$TEST_DB_NAME"
        print_message "$GREEN" "PostgreSQL test database created"
    else
        # SQLite setup
        print_message "$YELLOW" "Using SQLite for testing..."
        export TEST_DATABASE_URL="sqlite:///./test_migrations.db"

        # Remove existing test database
        rm -f test_migrations.db

        print_message "$GREEN" "SQLite test database prepared"
    fi
}

# Function to run migration integrity tests
run_migration_integrity_tests() {
    print_step "Running Migration Integrity Tests"

    if [ $VERBOSE -eq 1 ]; then
        pytest tests/test_migrations.py::TestMigrations::test_alembic_init -v
        pytest tests/test_migrations.py::TestMigrations::test_migration_chain_integrity -v
    else
        pytest tests/test_migrations.py::TestMigrations::test_alembic_init -q
        pytest tests/test_migrations.py::TestMigrations::test_migration_chain_integrity -q
    fi

    print_message "$GREEN" "Migration integrity tests passed"
}

# Function to run forward migration tests
run_forward_migration_tests() {
    print_step "Running Forward Migration Tests"

    if [ $VERBOSE -eq 1 ]; then
        pytest tests/test_migrations.py::TestMigrations::test_migrate_up_to_head -v
        pytest tests/test_migrations.py::TestMigrations::test_schema_validation -v
    else
        pytest tests/test_migrations.py::TestMigrations::test_migrate_up_to_head -q
        pytest tests/test_migrations.py::TestMigrations::test_schema_validation -q
    fi

    print_message "$GREEN" "Forward migration tests passed"
}

# Function to run rollback tests
run_rollback_tests() {
    print_step "Running Rollback Tests"

    if [ $VERBOSE -eq 1 ]; then
        pytest tests/test_migrations.py::TestMigrations::test_migrate_down_to_base -v
        pytest tests/test_migrations.py::TestMigrations::test_migration_up_down_up -v
    else
        pytest tests/test_migrations.py::TestMigrations::test_migrate_down_to_base -q
        pytest tests/test_migrations.py::TestMigrations::test_migration_up_down_up -q
    fi

    print_message "$GREEN" "Rollback tests passed"
}

# Function to run data preservation tests
run_data_preservation_tests() {
    print_step "Running Data Preservation Tests"

    if [ $VERBOSE -eq 1 ]; then
        pytest tests/test_migrations.py::TestMigrations::test_data_preservation_during_migration -v
        pytest tests/test_migrations.py::TestMigrations::test_migration_with_complex_data -v
    else
        pytest tests/test_migrations.py::TestMigrations::test_data_preservation_during_migration -q
        pytest tests/test_migrations.py::TestMigrations::test_migration_with_complex_data -q
    fi

    print_message "$GREEN" "Data preservation tests passed"
}

# Function to run performance tests
run_performance_tests() {
    print_step "Running Performance Tests"

    # Run migration performance tests
    if [ $VERBOSE -eq 1 ]; then
        pytest tests/test_migrations.py::TestMigrations::test_migration_performance -v
    else
        pytest tests/test_migrations.py::TestMigrations::test_migration_performance -q
    fi

    # Run database performance tests
    if [ $VERBOSE -eq 1 ]; then
        pytest tests/test_database_performance.py -v -k "performance"
    else
        pytest tests/test_database_performance.py -q -k "performance"
    fi

    print_message "$GREEN" "Performance tests completed"
}

# Function to test specific migration
test_specific_migration() {
    local migration_id=$1
    print_step "Testing Specific Migration: $migration_id"

    # Downgrade to before this migration
    alembic downgrade "$migration_id-1"

    # Upgrade to this migration
    alembic upgrade "$migration_id"

    # Run tests for this migration
    pytest tests/test_migrations.py::TestMigrationContent -k "$migration_id"

    print_message "$GREEN" "Migration $migration_id tested successfully"
}

# Function to run coverage tests
run_coverage_tests() {
    print_step "Running Tests with Coverage"

    pytest tests/test_migrations.py tests/test_database_performance.py \
        --cov=alembic \
        --cov=app/models \
        --cov=app/database \
        --cov-report=html:htmlcov_migrations \
        --cov-report=term-missing

    print_message "$GREEN" "Coverage report generated in htmlcov_migrations/"
}

# Function to validate current production state
validate_production_state() {
    print_step "Validating Production Migration State"

    # Get current revision
    CURRENT_REV=$(alembic current 2>/dev/null | grep -oE '[a-f0-9]{12}' || echo "none")

    if [ "$CURRENT_REV" == "none" ]; then
        print_message "$YELLOW" "Warning: No migrations applied to database"
    else
        print_message "$GREEN" "Current revision: $CURRENT_REV"
    fi

    # Check for pending migrations
    PENDING=$(alembic history --indicate-current 2>/dev/null | grep -c ">" || echo "0")

    if [ "$PENDING" -gt 0 ]; then
        print_message "$YELLOW" "Warning: There are $PENDING pending migrations"
        alembic history --indicate-current | head -20
    else
        print_message "$GREEN" "Database is up to date"
    fi
}

# Function to cleanup
cleanup() {
    print_step "Cleaning Up"

    # Remove test database if SQLite
    if [ -f test_migrations.db ]; then
        rm -f test_migrations.db
        print_message "$GREEN" "Removed test SQLite database"
    fi

    # Drop test PostgreSQL database if exists
    if command -v psql &> /dev/null && [ -n "$TEST_DATABASE_URL" ]; then
        if [[ $TEST_DATABASE_URL == *"$TEST_DB_NAME"* ]]; then
            # Parse TEST_DATABASE_URL
            DB_USER=$(echo $TEST_DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
            DB_HOST=$(echo $TEST_DATABASE_URL | sed -n 's/.*@\([^:\/]*\).*/\1/p')
            DB_PORT=$(echo $TEST_DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

            PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" 2>/dev/null || true
            print_message "$GREEN" "Removed test PostgreSQL database"
        fi
    fi

    print_message "$GREEN" "Cleanup completed"
}

# Function to generate report
generate_report() {
    print_step "Generating Test Report"

    REPORT_FILE="migration_test_report_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "Migration Test Report"
        echo "===================="
        echo "Date: $(date)"
        echo ""
        echo "Test Results:"
        echo "-------------"

        # Run pytest with JSON output for parsing
        pytest tests/test_migrations.py --json-report --json-report-file=.migration_test_results.json 2>/dev/null || true

        if [ -f .migration_test_results.json ]; then
            python -c "
import json
with open('.migration_test_results.json') as f:
    data = json.load(f)
    summary = data.get('summary', {})
    print(f\"Total tests: {summary.get('total', 0)}\")
    print(f\"Passed: {summary.get('passed', 0)}\")
    print(f\"Failed: {summary.get('failed', 0)}\")
    print(f\"Skipped: {summary.get('skipped', 0)}\")
"
            rm .migration_test_results.json
        fi

        echo ""
        echo "Current Database State:"
        echo "----------------------"
        alembic current 2>/dev/null || echo "Could not determine current state"

        echo ""
        echo "Migration History:"
        echo "-----------------"
        alembic history --verbose 2>/dev/null | head -20 || echo "Could not retrieve history"

    } > "$REPORT_FILE"

    print_message "$GREEN" "Report generated: $REPORT_FILE"
}

# Main execution
main() {
    print_message "$BLUE" "Starting Migration Test Suite"
    echo "=============================="

    # Check prerequisites
    check_prerequisites

    # Setup test environment
    setup_test_database

    # Run test suites
    run_migration_integrity_tests
    run_forward_migration_tests
    run_rollback_tests
    run_data_preservation_tests

    # Run performance tests if requested
    if [ $RUN_PERFORMANCE -eq 1 ]; then
        run_performance_tests
    fi

    # Run coverage if requested
    if [ $RUN_COVERAGE -eq 1 ]; then
        run_coverage_tests
    fi

    # Validate production state
    validate_production_state

    # Generate report
    generate_report

    # Cleanup
    cleanup

    print_message "$GREEN" ""
    print_message "$GREEN" "=========================================="
    print_message "$GREEN" "All migration tests completed successfully!"
    print_message "$GREEN" "=========================================="
}

# Trap errors and cleanup
trap 'cleanup; print_message "$RED" "Migration tests failed!"; exit 1' ERR

# Run main function
main

exit 0