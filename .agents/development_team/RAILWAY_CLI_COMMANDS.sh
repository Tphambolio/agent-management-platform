#!/bin/bash
# Railway CLI Commands - CrisisKit Deployment Helper
#
# This script provides useful Railway CLI commands for managing your deployment.
# You can run individual commands or use this as a reference.
#
# Prerequisites:
#   - Railway CLI installed: npm install -g @railway/cli
#   - Logged in: railway login
#   - Project linked: railway link

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if Railway CLI is installed
check_cli() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not installed"
        echo ""
        echo "Install with:"
        echo "  npm install -g @railway/cli"
        echo "  OR"
        echo "  brew install railway (Mac only)"
        exit 1
    fi
    print_success "Railway CLI is installed"
}

# Check if logged in and linked
check_auth() {
    if ! railway status &> /dev/null; then
        print_error "Not logged in or project not linked"
        echo ""
        echo "Run these commands:"
        echo "  railway login"
        echo "  railway link"
        exit 1
    fi
    print_success "Logged in and project linked"
}

#############################################
# 1. SETUP & INITIALIZATION
#############################################

setup_railway() {
    print_header "1. Setup Railway CLI"

    print_info "Installing Railway CLI..."
    npm install -g @railway/cli

    print_info "Logging in to Railway..."
    railway login

    print_info "Linking project..."
    cd /home/rpas/projects/crisiskit_project
    railway link

    print_success "Setup complete!"
}

#############################################
# 2. STATUS & INFORMATION
#############################################

show_status() {
    print_header "2. Service Status"
    railway status
}

show_variables() {
    print_header "3. Environment Variables"
    railway variables
    echo ""
    print_info "To check if DATABASE_URL exists:"
    railway variables | grep DATABASE_URL || print_error "DATABASE_URL not found!"
}

list_deployments() {
    print_header "4. Recent Deployments"
    print_info "This shows deployment history..."
    railway deployments
}

#############################################
# 3. DATABASE MANAGEMENT
#############################################

add_postgres() {
    print_header "5. Add PostgreSQL Database"
    print_info "Adding PostgreSQL to your project..."
    railway add --database postgres

    print_success "PostgreSQL added!"
    print_info "Waiting 10 seconds for provisioning..."
    sleep 10

    print_info "Checking if DATABASE_URL was added..."
    railway variables | grep DATABASE_URL && print_success "DATABASE_URL found!" || print_error "DATABASE_URL not found - check Railway dashboard"
}

check_database() {
    print_header "6. Database Connection Check"

    print_info "Checking if PostgreSQL service exists..."
    # Note: Railway CLI doesn't have a direct command to list services
    # Best to check via dashboard or logs

    print_info "Checking DATABASE_URL variable..."
    if railway variables | grep -q DATABASE_URL; then
        print_success "DATABASE_URL is set"
        railway variables | grep DATABASE_URL
    else
        print_error "DATABASE_URL not found!"
        echo ""
        echo "To add PostgreSQL:"
        echo "  railway add --database postgres"
        echo ""
        echo "OR use Railway Dashboard:"
        echo "  1. Go to https://railway.app/dashboard"
        echo "  2. Click your project"
        echo "  3. Click 'New' → 'Database' → 'Add PostgreSQL'"
    fi
}

#############################################
# 4. DEPLOYMENT OPERATIONS
#############################################

deploy_current() {
    print_header "7. Deploy Current Code"
    print_info "Deploying local changes to Railway..."
    railway up

    print_success "Deployment triggered!"
    print_info "Watching logs (Ctrl+C to exit)..."
    sleep 2
    railway logs --follow
}

redeploy_latest() {
    print_header "8. Redeploy Latest"
    print_info "Re-deploying without code changes..."
    railway redeploy

    print_success "Redeployment triggered!"
}

#############################################
# 5. LOGS & DEBUGGING
#############################################

show_logs() {
    print_header "9. View Recent Logs"
    print_info "Showing last 100 lines of logs..."
    railway logs --lines 100
}

follow_logs() {
    print_header "10. Follow Logs (Real-time)"
    print_info "Watching logs in real-time (Ctrl+C to exit)..."
    railway logs --follow
}

grep_logs() {
    local search_term=$1
    print_header "11. Search Logs"
    if [ -z "$search_term" ]; then
        print_error "No search term provided"
        echo "Usage: grep_logs 'search_term'"
        return 1
    fi

    print_info "Searching logs for: $search_term"
    railway logs --lines 500 | grep "$search_term" || print_error "No matches found"
}

check_health() {
    print_header "12. Test Health Endpoint"

    print_info "Getting service URL..."
    local url=$(railway status 2>/dev/null | grep -oP 'https://[^\s]+' || echo "")

    if [ -z "$url" ]; then
        print_error "Could not determine service URL"
        echo ""
        echo "Manually test with:"
        echo "  curl https://your-app.up.railway.app/health"
        return 1
    fi

    print_info "Testing: ${url}/health"
    curl -s "${url}/health" | python3 -m json.tool || print_error "Health check failed"
}

#############################################
# 6. CONFIGURATION MANAGEMENT
#############################################

set_variable() {
    local var_name=$1
    local var_value=$2

    print_header "13. Set Environment Variable"

    if [ -z "$var_name" ] || [ -z "$var_value" ]; then
        print_error "Usage: set_variable VAR_NAME 'var_value'"
        return 1
    fi

    print_info "Setting: $var_name"
    railway variables --set "$var_name=$var_value"
    print_success "Variable set!"

    print_info "Redeploy required for changes to take effect"
}

delete_variable() {
    local var_name=$1

    print_header "14. Delete Environment Variable"

    if [ -z "$var_name" ]; then
        print_error "Usage: delete_variable VAR_NAME"
        return 1
    fi

    print_info "Deleting: $var_name"
    railway variables --delete "$var_name"
    print_success "Variable deleted!"

    print_info "Redeploy required for changes to take effect"
}

#############################################
# 7. DIAGNOSTIC ROUTINES
#############################################

full_diagnostic() {
    print_header "15. Full Diagnostic Report"

    print_info "Collecting diagnostic information..."
    echo ""

    echo "=== Service Status ==="
    railway status
    echo ""

    echo "=== Environment Variables ==="
    railway variables
    echo ""

    echo "=== Recent Deployments ==="
    railway deployments | head -10
    echo ""

    echo "=== Recent Logs ==="
    railway logs --lines 50
    echo ""

    print_info "Checking critical variables..."
    echo "PORT: $(railway variables | grep -oP '(?<=PORT=).*' || echo 'Not set (Railway auto-injects)')"
    echo "DATABASE_URL: $(railway variables | grep -q DATABASE_URL && echo 'Set ✓' || echo 'Not set ✗')"
    echo ""

    print_info "Testing health endpoint..."
    local url=$(railway status 2>/dev/null | grep -oP 'https://[^\s]+' || echo "")
    if [ -n "$url" ]; then
        curl -s "${url}/health" | python3 -m json.tool || echo "Health check failed"
    else
        echo "Could not determine service URL"
    fi

    print_success "Diagnostic complete!"
}

quick_health_check() {
    print_header "16. Quick Health Check"

    echo -n "Service Status: "
    if railway status &>/dev/null; then
        print_success "Connected"
    else
        print_error "Failed"
        return 1
    fi

    echo -n "DATABASE_URL: "
    if railway variables | grep -q DATABASE_URL; then
        print_success "Set"
    else
        print_error "Missing"
    fi

    echo -n "Recent Errors: "
    local error_count=$(railway logs --lines 100 | grep -c -E "(ERROR|FATAL|Exception)" || echo "0")
    if [ "$error_count" -eq 0 ]; then
        print_success "None"
    else
        print_error "$error_count found"
    fi

    echo ""
}

#############################################
# 8. EMERGENCY PROCEDURES
#############################################

emergency_rollback() {
    print_header "17. Emergency Rollback"

    print_error "This will rollback to the previous deployment!"
    echo -n "Are you sure? (yes/no): "
    read -r confirm

    if [ "$confirm" != "yes" ]; then
        print_info "Rollback cancelled"
        return 0
    fi

    print_info "Rolling back..."
    railway rollback

    print_success "Rollback complete!"
    print_info "Checking status..."
    railway status
}

sqlite_fallback() {
    print_header "18. SQLite Fallback (Emergency)"

    print_error "⚠️  WARNING: This will DELETE the DATABASE_URL variable!"
    print_error "⚠️  All data will be LOST on next restart!"
    echo -n "Continue? (yes/no): "
    read -r confirm

    if [ "$confirm" != "yes" ]; then
        print_info "Cancelled"
        return 0
    fi

    print_info "Removing DATABASE_URL..."
    railway variables --delete DATABASE_URL || print_error "Failed to delete DATABASE_URL"

    print_info "Triggering redeploy..."
    railway redeploy

    print_error "App will now use SQLite (ephemeral storage)"
    print_info "To restore PostgreSQL, see: .agents/RAILWAY_POSTGRESQL_SETUP.md"
}

#############################################
# 9. EXPORT DIAGNOSTICS
#############################################

export_logs() {
    print_header "19. Export Logs to File"

    local filename="railway_logs_$(date +%Y%m%d_%H%M%S).txt"
    print_info "Exporting logs to: $filename"

    railway logs --lines 1000 > "$filename"
    print_success "Logs exported to: $filename"
}

export_full_report() {
    print_header "20. Export Full Diagnostic Report"

    local filename="railway_diagnostic_$(date +%Y%m%d_%H%M%S).txt"
    print_info "Generating full diagnostic report..."

    {
        echo "Railway Diagnostic Report"
        echo "Generated: $(date)"
        echo "Project: CrisisKit"
        echo "========================================"
        echo ""

        echo "=== Service Status ==="
        railway status
        echo ""

        echo "=== Environment Variables ==="
        railway variables
        echo ""

        echo "=== Recent Deployments ==="
        railway deployments
        echo ""

        echo "=== Recent Logs (Last 200 lines) ==="
        railway logs --lines 200
        echo ""

    } > "$filename"

    print_success "Full report exported to: $filename"
}

#############################################
# MAIN MENU
#############################################

show_menu() {
    print_header "Railway CLI Commands - CrisisKit"

    echo "Setup & Info:"
    echo "  1)  setup_railway          - Install CLI, login, link project"
    echo "  2)  show_status            - Show service status"
    echo "  3)  show_variables         - List environment variables"
    echo "  4)  list_deployments       - Show deployment history"
    echo ""
    echo "Database:"
    echo "  5)  add_postgres           - Add PostgreSQL database"
    echo "  6)  check_database         - Check database configuration"
    echo ""
    echo "Deployment:"
    echo "  7)  deploy_current         - Deploy local changes"
    echo "  8)  redeploy_latest        - Redeploy without changes"
    echo ""
    echo "Logs & Debugging:"
    echo "  9)  show_logs              - View recent logs"
    echo "  10) follow_logs            - Watch logs in real-time"
    echo "  11) grep_logs 'term'       - Search logs"
    echo "  12) check_health           - Test health endpoint"
    echo ""
    echo "Configuration:"
    echo "  13) set_variable NAME VAL  - Set environment variable"
    echo "  14) delete_variable NAME   - Delete environment variable"
    echo ""
    echo "Diagnostics:"
    echo "  15) full_diagnostic        - Run full diagnostic"
    echo "  16) quick_health_check     - Quick health check"
    echo ""
    echo "Emergency:"
    echo "  17) emergency_rollback     - Rollback to previous deployment"
    echo "  18) sqlite_fallback        - Switch to SQLite (DESTRUCTIVE)"
    echo ""
    echo "Export:"
    echo "  19) export_logs            - Save logs to file"
    echo "  20) export_full_report     - Save full diagnostic to file"
    echo ""
    echo "Usage:"
    echo "  source .agents/RAILWAY_CLI_COMMANDS.sh"
    echo "  show_menu                   # Show this menu"
    echo "  <function_name>             # Run any function above"
    echo ""
}

#############################################
# QUICK COMMANDS (Aliases)
#############################################

alias rw_status='show_status'
alias rw_logs='follow_logs'
alias rw_vars='show_variables'
alias rw_deploy='deploy_current'
alias rw_redeploy='redeploy_latest'
alias rw_health='check_health'
alias rw_diag='full_diagnostic'

#############################################
# AUTO-RUN
#############################################

# If script is executed (not sourced), show menu
if [ "${BASH_SOURCE[0]}" -eq "${0}" ]; then
    check_cli
    check_auth
    show_menu

    echo ""
    print_info "To use these commands, source this script:"
    echo "  source ${BASH_SOURCE[0]}"
    echo ""
    print_info "Or run individual commands:"
    echo "  bash ${BASH_SOURCE[0]} -c 'show_status'"
    echo "  bash ${BASH_SOURCE[0]} -c 'follow_logs'"
fi
