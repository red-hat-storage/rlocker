#!/bin/bash
# User Migration Helper Script for rlocker
# This script provides a convenient interface for exporting and importing users

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/venv"
MANAGE_PY="${SCRIPT_DIR}/manage.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  rlocker User Migration Tool${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

activate_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at: $VENV_PATH"
        print_info "Please create it first: python -m venv venv"
        exit 1
    fi

    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
}

check_dependencies() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found"
        exit 1
    fi

    if [ ! -f "$MANAGE_PY" ]; then
        print_error "manage.py not found at: $MANAGE_PY"
        exit 1
    fi
}

show_usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  export [FILE]           Export users to JSON file
                          Default file: users_export.json

  import [FILE]           Import users from JSON file
                          Default file: users_export.json

  preview [FILE]          Preview what would be imported (dry-run)

  backup [FILE]           Create timestamped backup
                          Default file: users_backup_YYYY-MM-DD_HH-MM-SS.json

  merge [FILE]            Import users but skip existing ones
                          Useful for merging two user databases

  status                  Show user/group statistics

  help                    Show this help message

Examples:
  $0 export                          # Export to users_export.json
  $0 export my_users.json            # Export to specific file
  $0 backup                          # Create timestamped backup
  $0 preview users_backup.json       # Preview import
  $0 import users_backup.json        # Import users
  $0 merge other_users.json          # Merge without overwriting

Options:
  You can also pass additional Django management command options:
  $0 export --pretty                 # Pretty-print JSON
  $0 import --ignore-tokens          # Don't import API tokens

EOF
}

export_users() {
    local output_file="${1:-users_export.json}"

    print_info "Exporting users to: $output_file"

    python "$MANAGE_PY" export_users -o "$output_file" --pretty

    if [ -f "$output_file" ]; then
        local size=$(du -h "$output_file" | cut -f1)
        print_success "Export complete: $output_file ($size)"
        print_warning "Secure this file - it contains password hashes and tokens!"
        echo
        print_info "To transfer to another server:"
        echo "  scp $output_file user@server:/path/to/rlocker/"
    else
        print_error "Export failed - file not created"
        exit 1
    fi
}

import_users() {
    local input_file="${1:-users_export.json}"

    if [ ! -f "$input_file" ]; then
        print_error "File not found: $input_file"
        exit 1
    fi

    print_warning "This will modify the database!"
    print_info "Importing from: $input_file"
    echo

    read -p "Continue with import? [y/N] " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Import cancelled"
        exit 0
    fi

    python "$MANAGE_PY" import_users -i "$input_file"

    print_success "Import complete!"
}

preview_import() {
    local input_file="${1:-users_export.json}"

    if [ ! -f "$input_file" ]; then
        print_error "File not found: $input_file"
        exit 1
    fi

    print_info "Previewing import from: $input_file"
    print_info "No changes will be made"
    echo

    python "$MANAGE_PY" import_users -i "$input_file" --dry-run
}

backup_users() {
    local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
    local output_file="${1:-users_backup_${timestamp}.json}"

    print_info "Creating backup: $output_file"

    export_users "$output_file"
}

merge_users() {
    local input_file="${1:-users_export.json}"

    if [ ! -f "$input_file" ]; then
        print_error "File not found: $input_file"
        exit 1
    fi

    print_info "Merging users from: $input_file"
    print_info "Existing users will be skipped (not updated)"
    echo

    read -p "Continue with merge? [y/N] " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Merge cancelled"
        exit 0
    fi

    python "$MANAGE_PY" import_users -i "$input_file" --skip-existing

    print_success "Merge complete!"
}

show_status() {
    print_info "Database Statistics"
    echo

    python "$MANAGE_PY" shell << 'EOF'
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

total_users = User.objects.count()
active_users = User.objects.filter(is_active=True).count()
staff_users = User.objects.filter(is_staff=True).count()
superusers = User.objects.filter(is_superuser=True).count()
total_groups = Group.objects.count()
total_tokens = Token.objects.count()

print(f"Users:")
print(f"  Total:      {total_users}")
print(f"  Active:     {active_users}")
print(f"  Staff:      {staff_users}")
print(f"  Superuser:  {superusers}")
print(f"\nGroups:       {total_groups}")
print(f"Tokens:       {total_tokens}")

if total_groups > 0:
    print(f"\nGroup Names:")
    for group in Group.objects.all():
        member_count = group.user_set.count()
        print(f"  - {group.name} ({member_count} members)")
EOF

    echo
}

# Main script
main() {
    print_header

    check_dependencies
    activate_venv

    echo

    local command="${1:-help}"
    shift || true

    case "$command" in
        export)
            export_users "$@"
            ;;
        import)
            import_users "$@"
            ;;
        preview)
            preview_import "$@"
            ;;
        backup)
            backup_users "$@"
            ;;
        merge)
            merge_users "$@"
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
