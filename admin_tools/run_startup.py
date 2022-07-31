# This file loads up for ONE TIME once the application
# is being recognized as an INSTALLED_APP (INSTALLED_ADDON)
# Use this file to add code that should be executed first time

from admin_tools.models import Addon

def main():
    Addon.insert_supported_addons()
