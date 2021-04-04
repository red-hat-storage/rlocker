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


class Status:
    PENDING = 'PENDING' # describes that it still waits to be assigned to a lockable resource
    FINISHED = 'FINISHED' # describes that it locked a lockable resource successfully
    FAILED = 'FAILED' # describes that it attempted to lock a resource but failed
    ABORTED = 'ABORTED' # describes a failure to lock a resource because of manual interruption


    # We also need to customize all the options in a way that is supportive in Django dropdown field:
    # TODO: Create a generic list of tuples depending on the values above!
    CHOICES = [
        (PENDING, 'PENDING'),
        (FINISHED, 'FINISHED'),
        (FAILED, 'FAILED'),
        (ABORTED, 'ABORTED')
    ]

