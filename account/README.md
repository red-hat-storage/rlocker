# Account App

This Django app handles user account management and authentication for rlocker.

## Features

- Automatic API token generation for new users (via Django signals)
- User account creation and management
- Integration with Django REST Framework token authentication

## Management Commands

### create_accounts
Interactive command for creating multiple user accounts at once.

**Usage:**
```bash
python manage.py create_accounts
```

This will prompt for:
- List of usernames (comma-separated)
- Initial password for all users
- Groups to add users to

### retrieve_token
Get the API token for a specific user.

**Usage:**
```bash
python manage.py retrieve_token -u USERNAME
```

**Example:**
```bash
python manage.py retrieve_token -u alice
# Output: a1b2c3d4e5f6...
```

### export_users
Export users, groups, and API tokens to a JSON file for migration.

**Usage:**
```bash
python manage.py export_users [-o OUTPUT_FILE] [--pretty]
```

**Options:**
- `-o FILE`, `--output FILE` - Output file path (default: users_export.json)
- `--pretty` - Format JSON with indentation

**Example:**
```bash
python manage.py export_users -o backup.json --pretty
```

See [USER_MIGRATION_GUIDE.md](../USER_MIGRATION_GUIDE.md) for details.

### import_users
Import users, groups, and API tokens from a JSON file.

**Usage:**
```bash
python manage.py import_users [-i INPUT_FILE] [OPTIONS]
```

**Options:**
- `-i FILE`, `--input FILE` - Input file path (default: users_export.json)
- `--skip-existing` - Skip users that already exist
- `--dry-run` - Preview changes without making them
- `--ignore-tokens` - Don't import API tokens

**Example:**
```bash
# Preview import
python manage.py import_users -i backup.json --dry-run

# Actual import
python manage.py import_users -i backup.json
```

See [USER_MIGRATION_GUIDE.md](../USER_MIGRATION_GUIDE.md) for details.

## Signals

### create_token_once_user_registers
Automatically creates an API token whenever a new user is created.

**Signal:** `post_save` on `User` model
**Handler:** `account.signals.create_token_once_user_registers`

This ensures every user has an API token for REST API authentication.

## Authentication

This app works with Django REST Framework's token authentication:

```python
# In API views
from api.custom_permissions import HasValidTokenOrIsAuthenticated

@permission_classes([HasValidTokenOrIsAuthenticated])
def my_api_view(request):
    # Users can authenticate via:
    # 1. Session authentication (logged in via web)
    # 2. Token authentication (header: Authorization: Token <key>)
    pass
```

## Migration Helper

For easy user migration between rlocker instances, use the helper script:

```bash
# Export users
./migrate_users.sh export

# Import users
./migrate_users.sh import users_export.json

# See all options
./migrate_users.sh help
```

See [USER_MIGRATION_GUIDE.md](../USER_MIGRATION_GUIDE.md) for complete migration documentation.
