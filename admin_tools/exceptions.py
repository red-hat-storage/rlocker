# Custom exceptions for admin_tools
# TODO Possibly improve the exception classes and move them to a common location across all applications ?
from django.core import management


class ApplicationNotMigratedException(Exception):
    def __init__(self, app_name):
        self.app_name = app_name

        self.attempt_fix()

    def attempt_fix(self):
        """
        Run section of commands that will provide fix for the problem
        """
        print(f"Executing python manage.py migrate {self.app_name}")
        management.call_command("migrate", self.app_name)

    def __str__(self):
        return f"The Application {self.app_name} not migrated yet!"
