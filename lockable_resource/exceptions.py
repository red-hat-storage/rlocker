#Exceptions that are used with in the lockable_resource app

class AlreadyLockedException(Exception):
    def __init__(self):
        print("The Lockable Resource you are trying to Lock is already Locked!")

class AlreadyFreeException(Exception):
    def __init__(self):
        print("The Lockable Resource you are trying to Release is already Free!")

class FreeResourceNotAvailableException(Exception):
    def __init__(self, attempted_string):
        print(f"There are no free resources available that matches a label or a name: {attempted_string}")

class LockWithoutSignoffException(Exception):
    def __init__(self, obj):
        print(f"Cannot lock resource {obj.name} without signoff. "
              "Please provide a signoff!")