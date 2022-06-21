from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Command for creating accounts that are not existing on the platform"

    def add_user_to_groups(self, user, list_of_groups):
        """
        :param user: User Object
        :param list_of_groups: List of Group Names
        :return: None
        """
        for group in list_of_groups:
            group = Group.objects.get(name=group)
            group.user_set.add(user)
            print(f"User added to group -> {group}")

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Create all the users provided in the list

        :return: None
        """

        list_of_users = input("List of Users ? Comma Separated (Without spacing)\n")
        list_of_users = list_of_users.split(",")
        initial_password = input(
            "Decide initial password for all the users, they can change it in the first login\n"
        )
        list_of_groups = input(
            "List of Groups ? Comma Separated (Without spacing) \n"
            f"List of all groups: \n"
            f"{Group.objects.all()} \n"
        )
        list_of_groups = list_of_groups.split(",") if list_of_groups != "" else []

        for user in list_of_users:
            try:
                existing_user = User.objects.get(username=user)
                print(f"{user} exists! skipping ...")
                self.add_user_to_groups(existing_user, list_of_groups)

            except User.DoesNotExist:
                # If we are here, it means that the User objects does not exist, let's create it
                new_user = User.objects.create_user(user, password=initial_password)
                self.add_user_to_groups(new_user, list_of_groups)
                new_user.save()
                print(f"User {user} created successfully!")
