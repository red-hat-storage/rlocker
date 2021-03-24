from rqueue.models import Rqueue, FinishedQueue
def run():
    '''
        Delete all Finished and Pending Queues

    :return: None
    '''

    Rqueue.objects.all().delete()
    print('Pending Queues have been deleted')


    FinishedQueue.objects.all().delete()
    print('Finished Queue have been deleted')