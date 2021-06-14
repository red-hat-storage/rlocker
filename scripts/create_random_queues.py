import pprint as pp
import time
from rqueue.models import Rqueue


def generate(priority, json_data, quantity):
    for i in range(quantity):
        r = Rqueue(
            priority=priority,
            data=json_data,
        )
        r.save()
        print("GENERATED: \n")
        pp.pprint(r.data)
        time.sleep(1)

    return None


def run():
    """
    Generate random queues in order to test the application

    :return: None
    """
    generate(priority=2, json_data='{"label":"aws", "username":"jsc"}', quantity=1)
    generate(
        priority=4,
        json_data='{"id":102 ,"name":"vsphere-resource-2", "username":"jsc"}',
        quantity=4,
    )
    generate(priority=2, json_data='{"label":"gcp", "username":"jsc"}', quantity=6)
