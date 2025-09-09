# Constants that are used with in the lockable_resource app
STATUS_LOCKED = "LOCKED"
STATUS_FREE = "FREE"
STATUS_MAINTENANCE = "MAINTENANCE"

ACTION_LOCK = "lock"
ACTION_RELEASE = "release"

ACTION_MAINTENANCE_MODE_ENTER = "maintenance_mode_enter"
ACTION_MAINTENANCE_MODE_EXIT = "maintenance_mode_exit"


class LockMethod:
    MANUAL = "manual"
    AUTO = "auto"
