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

class InvalidLabelException(Exception):
    #Raised when the given label does not exist in the platform!
    #This should only be raised when we try to instantiate LabelManager
    #Because before we instantiate it, we should validate if the given label even exists
    #in the entire platform!
    def __init__(self, label):
        print(f"Invalid Label {label}. This label does not exists across all the lockable resources"
              f"Cannot recover from this error."
              f"Request is NOT entering to QUEUE")