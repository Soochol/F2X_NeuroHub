#!/bin/bash
# =============================================================================
# F2X NeuroHub MES - Deployment Script
# Usage: ./deploy.sh [command]
# Commands: start, stop, restart, logs, status, migrate, build
# =============================================================================

set -e

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.production exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env.production file not found!"
        log_info "Copy .env.production.example to .env.production and update values"
        exit 1
    fi
}

# Build images
build() {
    log_info "Building Docker images..."
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE build
    log_info "Build completed!"
}

# Start services
start() {
    check_env
    log_info "Starting F2X NeuroHub MES..."
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    log_info "Services started!"
    log_info "Access the application at http://localhost"
}

# Stop services
stop() {
    log_info "Stopping F2X NeuroHub MES..."
    docker-compose -f $COMPOSE_FILE down
    log_info "Services stopped!"
}

# Restart services
restart() {
    stop
    start
}

# Show logs
logs() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        docker-compose -f $COMPOSE_FILE logs -f
    else
        docker-compose -f $COMPOSE_FILE logs -f $SERVICE
    fi
}

# Show status
status() {
    log_info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
}

# Run database migrations
migrate() {
    log_info "Running database migrations..."
    docker-compose -f $COMPOSE_FILE exec backend alembic upgrade head
    log_info "Migrations completed!"
}

# Full deployment (build + start + migrate)
deploy() {
    check_env
    log_info "Starting full deployment..."
    build
    start
    log_info "Waiting for services to be ready..."
    sleep 10
    migrate
    log_info "Deployment completed!"
    status
}

# Clean up (remove containers, networks, volumes)
clean() {
    log_warn "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE down -v --rmi local
        log_info "Cleanup completed!"
    fi
}

# Help
help() {
    echo "F2X NeuroHub MES - Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  build     - Build Docker images"
    echo "  deploy    - Full deployment (build + start + migrate)"
    echo "  migrate   - Run database migrations"
    echo "  logs      - Show logs (optionally specify service: logs backend)"
    echo "  status    - Show service status"
    echo "  clean     - Remove all containers and volumes"
    echo "  help      - Show this help"
}

# Main
case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    build)
        build
        ;;
    deploy)
        deploy
        ;;
    migrate)
        migrate
        ;;
    logs)
        logs $2
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|*)
        help
        ;;
esac
