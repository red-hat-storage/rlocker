from django.contrib.auth.models import Permission, User


def run(
        list_of_users=None,
        initial_password=None,
        list_of_perms=None
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

    if not list_of_perms:
        list_of_perms = input("List of Permissions ? Comma Separated (Without spacing)")
        list_of_perms = list_of_perms.split(',')

    for user in list_of_users:
        try:
            User.objects.get(username=user)
            print(f"{user} exists! skipping ...")
        except User.DoesNotExist:
            # If we are here, it means that the User objects does not exist, let's create it
            create_attempt = User.objects.create_user(
                user, password=initial_password
            )
            for perm in list_of_perms:
                perm_object = Permission.objects.get(name=perm)
                create_attempt.user_permissions.add(perm_object)

            create_attempt.save()
            print(f"User {user} created successfully!")



