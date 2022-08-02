from django.core.management.base import BaseCommand
from admin_tools.models import Addon
from django.conf import settings


class Command(BaseCommand):
    help = "Check the installed addons and write them to a file so the settings.py could recognize them"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Method will filter the installed addons and write
            their application names to a file
        """
        installed_addons = Addon.get_installed_addons(key="application_name")
        if not settings.USE_DEV_ADDONS:
            print(f"FOUND {len(installed_addons)} addons to finalize installation. ")
            print(
                "Django will write a new file to {settings.ADDONS_FILE} with all the installed addons if there are any."
            )
            with open(settings.ADDONS_FILE, "w") as f:
                for installed_addon in installed_addons:
                    f.write(installed_addon)
                    print(f"WRITTEN: {installed_addon}")
