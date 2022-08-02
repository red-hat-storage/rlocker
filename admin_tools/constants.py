import os
from rlocker import settings


SUPPORTED_ADDONS_FILE = os.path.join(
    settings.BASE_DIR, "admin_tools", "supported_addons.yaml"
)

ACTION_INSTALL_ADDON = "install_addon"
ACTION_UNINSTALL_ADDON = "uninstall_addon"