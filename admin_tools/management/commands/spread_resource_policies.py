from django.core.management.base import BaseCommand
from expiry_addon.models import ResourceExpiryPolicy
from lockable_resource.models import LockableResource
from lockable_resource.label_manager import LabelManager


class Command(BaseCommand):
    help = "Create policies for given group of resources, based on label"

    def add_arguments(self, parser):
        parser.add_argument("-l", "--label", type=str, required=True)
        parser.add_argument("-hr", "--hour", type=int, required=True)
        parser.add_argument(
            "-exl", "--exclude-locked", type=bool, required=False, default=True
        )

    def handle(self, *args, **options):
        """
        Create Resource Policies
        :return: None
        """

        # Run Validations:
        label = options.get("label")
        lbl_manager = LabelManager(label)  # This validates that the label exists

        hour = options.get("hour")
        exclude_locked = options.get("exclude_locked")

        resources_to_spread = (
            lbl_manager.free_resources if exclude_locked else lbl_manager.all_resources
        )
        # Save a separated line version for showing in the confirmation message
        resources_line_separated = "\n".join(map(str, resources_to_spread))

        print(f"The following resources are going to have a policy to be expired after {hour} hours:")
        print(resources_line_separated)
        answer = input("\n Press 'Y/y' to confirm")

        if answer.lower() == "y":
            for resource in resources_to_spread:
                # Create a policy
                policy = ResourceExpiryPolicy(
                    lockable_resource=resource, expiry_hour=hour
                )
                policy.save()
                print(f"Policy: {policy} created!")
        else:
            print("Operation canceled.")
