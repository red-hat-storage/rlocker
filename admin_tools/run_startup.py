# This file loads up for ONE TIME once the application
# is being recognized as an INSTALLED_APP (INSTALLED_ADDON)
# Use this file to add code that should be executed first time

import sys
from admin_tools.models import Addon


def insert_supported_addons_on_runserver():
    """
    Run this chunk of command only on runserver
    """
    sub_command = sys.argv[1]
    if sub_command == "runserver":
        Addon.insert_supported_addons()
    else:
        pass


def main():
    insert_supported_addons_on_runserver()
