#!/bin/bash

# Arthachitra Production Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ENVIRONMENT=${1:-production}
VERSION=${2:-latest}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_step "Running pre-deployment checks..."
    
    # Check if we're on the correct branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$ENVIRONMENT" == "production" && "$CURRENT_BRANCH" != "main" ]]; then
        log_error "Production deployments must be from 'main' branch"
        log_error "Current branch: $CURRENT_BRANCH"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_error "There are uncommitted changes. Please commit or stash them."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required for deployment"
        exit 1
    fi
    
    # Check kubectl for K8s deployment
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is required for Kubernetes deployment"
        exit 1
    fi
    
    log_info "Pre-deployment checks passed ✅"
}

# Build and push Docker images
build_and_push_images() {
    log_step "Building and pushing Docker images..."
    
    # Set image registry
    REGISTRY="ghcr.io/yourusername/arthachitra"
    
    # Build frontend
    log_info "Building frontend image..."
    docker build -t "$REGISTRY/frontend:$VERSION" -f Dockerfile.frontend .
    docker push "$REGISTRY/frontend:$VERSION"
    
    # Build backend
    log_info "Building backend image..."
    docker build -t "$REGISTRY/backend:$VERSION" -f Dockerfile.backend .
    docker push "$REGISTRY/backend:$VERSION"
    
    # Build ML service
    log_info "Building ML service image..."
    docker build -t "$REGISTRY/ml:$VERSION" -f Dockerfile.ml .
    docker push "$REGISTRY/ml:$VERSION"
    
    # Build tick engine
    log_info "Building tick engine image..."
    docker build -t "$REGISTRY/tick-engine:$VERSION" -f Dockerfile.tickengine .
    docker push "$REGISTRY/tick-engine:$VERSION"
    
    log_info "Docker images built and pushed ✅"
}

# Update Kubernetes manifests
update_k8s_manifests() {
    log_step "Updating Kubernetes manifests..."
    
    # Update image versions in deployment files
    find deploy/kubernetes/$ENVIRONMENT -name "*.yaml" -exec \
        sed -i "s|image: .*arthachitra/|image: ghcr.io/yourusername/arthachitra/|g; s|:latest|:$VERSION|g" {} \;
    
    log_info "Kubernetes manifests updated ✅"
}

# Deploy to Kubernetes
deploy_to_k8s() {
    log_step "Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace arthachitra-$ENVIRONMENT --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations in order
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/configmap.yaml
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/secrets.yaml
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/postgres.yaml
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/redis.yaml
    
    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n arthachitra-$ENVIRONMENT --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n arthachitra-$ENVIRONMENT --timeout=300s
    
    # Deploy application services
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/backend.yaml
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/ml.yaml
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/tick-engine.yaml
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/frontend.yaml
    
    # Wait for deployments to be ready
    log_info "Waiting for application services to be ready..."
    kubectl wait --for=condition=available deployment -l tier=backend -n arthachitra-$ENVIRONMENT --timeout=600s
    kubectl wait --for=condition=available deployment -l tier=frontend -n arthachitra-$ENVIRONMENT --timeout=600s
    
    # Apply ingress
    kubectl apply -f deploy/kubernetes/$ENVIRONMENT/ingress.yaml
    
    log_info "Kubernetes deployment completed ✅"
}

# Run database migrations
run_migrations() {
    log_step "Running database migrations..."
    
    # Get backend pod name
    BACKEND_POD=$(kubectl get pods -n arthachitra-$ENVIRONMENT -l app=backend -o jsonpath='{.items[0].metadata.name}')
    
    if [ -n "$BACKEND_POD" ]; then
        kubectl exec -n arthachitra-$ENVIRONMENT $BACKEND_POD -- python -m alembic upgrade head
        log_info "Database migrations completed ✅"
    else
        log_error "Could not find backend pod for migrations"
        exit 1
    fi
}

# Health checks
run_health_checks() {
    log_step "Running health checks..."
    
    # Get service URLs
    if [[ "$ENVIRONMENT" == "production" ]]; then
        FRONTEND_URL="https://arthachitra.com"
        BACKEND_URL="https://api.arthachitra.com"
    else
        FRONTEND_URL="https://staging.arthachitra.com"
        BACKEND_URL="https://api-staging.arthachitra.com"
    fi
    
    # Check frontend
    log_info "Checking frontend health..."
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        log_info "Frontend health check passed ✅"
    else
        log_error "Frontend health check failed ❌"
        exit 1
    fi
    
    # Check backend
    log_info "Checking backend health..."
    if curl -f -s "$BACKEND_URL/health" > /dev/null; then
        log_info "Backend health check passed ✅"
    else
        log_error "Backend health check failed ❌"
        exit 1
    fi
    
    log_info "All health checks passed ✅"
}

# Send deployment notification
send_notification() {
    log_step "Sending deployment notification..."
    
    SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
    
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 Arthachitra $ENVIRONMENT deployment completed successfully! Version: $VERSION\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1
        log_info "Slack notification sent ✅"
    fi
    
    # Email notification (if configured)
    NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"
    if [ -n "$NOTIFICATION_EMAIL" ]; then
        echo "Arthachitra $ENVIRONMENT deployment completed successfully! Version: $VERSION" | \
            mail -s "Deployment Notification" "$NOTIFICATION_EMAIL" || true
    fi
}

# Main deployment function
main() {
    echo "🚀 Starting Arthachitra $ENVIRONMENT deployment..."
    echo "Version: $VERSION"
    echo "Time: $(date)"
    echo "========================================="
    
    # Confirm production deployment
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_warn "You are about to deploy to PRODUCTION"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Run deployment steps
    pre_deployment_checks
    build_and_push_images
    update_k8s_manifests
    deploy_to_k8s
    run_migrations
    run_health_checks
    send_notification
    
    echo "========================================="
    log_info "🎉 Arthachitra $ENVIRONMENT deployment completed successfully!"
    log_info "Frontend: $(kubectl get ingress -n arthachitra-$ENVIRONMENT -o jsonpath='{.items[0].spec.rules[0].host}')"
    log_info "Backend: $(kubectl get ingress -n arthachitra-$ENVIRONMENT -o jsonpath='{.items[0].spec.rules[1].host}')"
    log_info "Version: $VERSION"
    log_info "Deployed at: $(date)"
    echo "========================================="
}

# Run main function
main "$@"
