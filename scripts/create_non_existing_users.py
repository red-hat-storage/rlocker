from django.contrib.auth.models import User, Group


def run(
        list_of_users=None,
        initial_password=None,
        list_of_groups=None
):
    """
    Create all the users provided in the list

    :return: None
    """
    if not list_of_users:
        list_of_users = input("List of Users ? Comma Separated (Without spacing)")
        list_of_users = list_of_users.split(',')

    if not initial_password:
        initial_password = input("Decide initial password for all the users, they can change it in the first login")

    if not list_of_groups:
        list_of_groups = input("List of Groups ? Comma Separated (Without spacing) \n"
                               f"List of all groups: \n"
                               f"{Group.objects.all()}")
        list_of_groups = list_of_groups.split(',') if list_of_groups != '' else []

    for user in list_of_users:
        try:
            existing_user = User.objects.get(username=user)
            print(f"{user} exists! skipping ...")
            if len(list_of_groups) > 0:
                for group in list_of_groups:
                    group = Group.objects.get(name=group)
                    group.user_set.add(existing_user)
                    print(f"User added to group -> {group}")

        except User.DoesNotExist:
            # If we are here, it means that the User objects does not exist, let's create it
            create_attempt = User.objects.create_user(
                user, password=initial_password
            )
            if len(list_of_groups) > 0:
                for group in list_of_groups:
                    group = Group.objects.get(name=group)
                    group.user_set.add(create_attempt)
                    print(f"User added to group -> {group}")
            create_attempt.save()
            print(f"User {user} created successfully!")



