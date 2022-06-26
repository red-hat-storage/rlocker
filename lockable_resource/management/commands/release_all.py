from django.core.management.base import BaseCommand
from lockable_resource.models import LockableResource


class Command(BaseCommand):
    help = "Command for Releasing all resources"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
            Release all lockable resources
        :return: None
        """
        confirmation = input(
            "Confirm ? " "This will release all the locked resources. Y/N"
        )
        if confirmation.lower() == "y":
            for lr in LockableResource.objects.all():
                try:
                    lr.release()
                except:
                    print(f"Skipping {lr.name}. It is released ...")

            print("All Lockable resources have been released!")
