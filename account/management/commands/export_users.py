from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
import json


class Command(BaseCommand):
    help = "Export users, groups, and tokens to JSON file for migration"

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            default="users_export.json",
            help="Output JSON file path (default: users_export.json)",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Format JSON with indentation for readability",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        pretty = options["pretty"]

        # Export groups
        groups_data = []
        for group in Group.objects.all():
            groups_data.append(
                {
                    "id": group.id,
                    "name": group.name,
                }
            )

        # Export users
        users_data = []
        for user in User.objects.all():
            try:
                token = Token.objects.get(user=user).key
            except Token.DoesNotExist:
                token = None

            users_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "password": user.password,  # Already hashed
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "token": token,
                    "groups": [g.name for g in user.groups.all()],
                }
            )

        # Combine all data
        export_data = {
            "export_metadata": {
                "version": "1.0",
                "exported_at": __import__("datetime").datetime.now().isoformat(),
            },
            "groups": groups_data,
            "users": users_data,
        }

        # Write to file
        with open(output_file, "w") as f:
            if pretty:
                json.dump(export_data, f, indent=2)
            else:
                json.dump(export_data, f)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nExport complete:\n"
                f"  File: {output_file}\n"
                f"  Groups: {len(groups_data)}\n"
                f"  Users: {len(users_data)}\n"
                f"  Tokens: {sum(1 for u in users_data if u['token'])}"
            )
        )
