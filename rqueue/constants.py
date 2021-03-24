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