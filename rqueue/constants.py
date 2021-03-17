from enum import Enum

class Priority(Enum):
    '''
        Class designed for having a set of priorities
        If a resource is requested to lock from the UI, it means
            that it is ready to be locked immediately.
        But if a resource is requested to retrieve from search_string,
            then it should include the priority level from 1-3
         - UI
         - LIVE_TESTING
         - PRODUCTION_RUN
         - DEVELOPMENT_RUN
    '''
    UI = 0
    LIVE_TESTING = 1
    PRODUCTION_RUN = 2
    DEVELOPMENT_RUN = 3

class Interval:
    RESOURCE_FREE_WAIT = 10
    QUEUE_TURN_WAIT = 30

REQUEST_TIMEOUT = 600