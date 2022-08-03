# This file loads up for ONE TIME once the application
# is being recognized as an INSTALLED_APP (INSTALLED_ADDON)
# Use this file to add code that should be executed first time

import sys
from django.db import utils as django_utils
from admin_tools.models import Addon
from admin_tools.exceptions import ApplicationNotMigratedException
from admin_tools.apps import AdminToolsConfig
from retry import retry


@retry(ApplicationNotMigratedException, tries=2, delay=5)
def insert_supported_addons_on_runserver():
    """
    Run this chunk of command only on runserver
    TODO: Add retry because although we want to have this in runserver, the Model might not be migrated, after first failure, worth to run migrate admin_tools and then runserver
    """
    sub_command = sys.argv[1]
    if sub_command == "runserver":
        try:
            Addon.insert_supported_addons()
        except django_utils.ProgrammingError:
            raise ApplicationNotMigratedException(AdminToolsConfig.name)
    else:
        pass


def main():
    insert_supported_addons_on_runserver()
