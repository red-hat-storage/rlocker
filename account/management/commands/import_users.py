from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from django.db import transaction
from datetime import datetime
import json


class Command(BaseCommand):
    help = "Import users, groups, and tokens from JSON file for migration"

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--input",
            type=str,
            default="users_export.json",
            help="Input JSON file path (default: users_export.json)",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip users that already exist (default: update them)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without making changes",
        )
        parser.add_argument(
            "--ignore-tokens",
            action="store_true",
            help="Don't import tokens (new tokens will be auto-generated)",
        )

    def handle(self, *args, **options):
        input_file = options["input"]
        skip_existing = options["skip_existing"]
        dry_run = options["dry_run"]
        ignore_tokens = options["ignore_tokens"]

        # Read import file
        try:
            with open(input_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"File not found: {input_file}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON file: {e}")

        # Validate file structure
        if "users" not in data:
            raise CommandError("Invalid export file: missing 'users' key")
        if "groups" not in data:
            raise CommandError("Invalid export file: missing 'groups' key")

        groups_data = data["groups"]
        users_data = data["users"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n=== DRY RUN MODE ===\n"
                    f"Would import:\n"
                    f"  Groups: {len(groups_data)}\n"
                    f"  Users: {len(users_data)}\n"
                )
            )

        # Import with transaction
        try:
            with transaction.atomic():
                # Import groups first
                groups_created = 0
                groups_existing = 0

                for group_data in groups_data:
                    group_name = group_data["name"]

                    if dry_run:
                        if Group.objects.filter(name=group_name).exists():
                            groups_existing += 1
                        else:
                            groups_created += 1
                        continue

                    group, created = Group.objects.get_or_create(name=group_name)
                    if created:
                        groups_created += 1
                        self.stdout.write(f"  Created group: {group_name}")
                    else:
                        groups_existing += 1

                # Import users
                users_created = 0
                users_updated = 0
                users_skipped = 0
                tokens_created = 0
                tokens_updated = 0

                for user_data in users_data:
                    username = user_data["username"]

                    try:
                        user = User.objects.get(username=username)

                        if skip_existing:
                            users_skipped += 1
                            if not dry_run:
                                self.stdout.write(f"  Skipped existing: {username}")
                            continue

                        # Update existing user
                        if not dry_run:
                            user.password = user_data["password"]
                            user.email = user_data["email"]
                            user.first_name = user_data["first_name"]
                            user.last_name = user_data["last_name"]
                            user.is_staff = user_data["is_staff"]
                            user.is_superuser = user_data["is_superuser"]
                            user.is_active = user_data["is_active"]

                            if user_data["last_login"]:
                                user.last_login = datetime.fromisoformat(
                                    user_data["last_login"]
                                )

                            user.save()
                            self.stdout.write(f"  Updated user: {username}")

                        users_updated += 1

                    except User.DoesNotExist:
                        # Create new user
                        if not dry_run:
                            user = User(
                                username=username,
                                password=user_data["password"],  # Already hashed
                                email=user_data["email"],
                                first_name=user_data["first_name"],
                                last_name=user_data["last_name"],
                                is_staff=user_data["is_staff"],
                                is_superuser=user_data["is_superuser"],
                                is_active=user_data["is_active"],
                                date_joined=datetime.fromisoformat(
                                    user_data["date_joined"]
                                ),
                            )

                            if user_data["last_login"]:
                                user.last_login = datetime.fromisoformat(
                                    user_data["last_login"]
                                )

                            user.save()
                            self.stdout.write(
                                self.style.SUCCESS(f"  Created user: {username}")
                            )

                        users_created += 1

                    # Handle groups
                    if not dry_run:
                        user.groups.clear()
                        for group_name in user_data["groups"]:
                            try:
                                group = Group.objects.get(name=group_name)
                                user.groups.add(group)
                            except Group.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"    Group not found: {group_name}, skipping"
                                    )
                                )

                    # Handle token
                    if not ignore_tokens and user_data["token"]:
                        if not dry_run:
                            token, created = Token.objects.update_or_create(
                                user=user, defaults={"key": user_data["token"]}
                            )

                            if created:
                                tokens_created += 1
                            else:
                                tokens_updated += 1

                # If dry run, rollback transaction
                if dry_run:
                    transaction.set_rollback(True)

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

        # Summary
        summary = (
            f"\n{'DRY RUN - ' if dry_run else ''}Import complete:\n"
            f"  Groups: {groups_created} created, {groups_existing} already existed\n"
            f"  Users: {users_created} created, {users_updated} updated, {users_skipped} skipped\n"
        )

        if not ignore_tokens:
            summary += (
                f"  Tokens: {tokens_created} created, {tokens_updated} updated\n"
            )
        else:
            summary += f"  Tokens: skipped (will be auto-generated on first save)\n"

        if dry_run:
            summary += "\nNo changes were made (dry run mode)\n"

        self.stdout.write(self.style.SUCCESS(summary))
