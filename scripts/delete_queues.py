from rqueue.models import Rqueue
def run():
    '''
        Delete all Rqueues

    :return: None
    '''

    Rqueue.objects.all().delete()
    print('RQueue objects have been deleted')