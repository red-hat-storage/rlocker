from lockable_resource.models import LockableResource


def run():
    """
        Release all lockable resources

    :return: None
    """

    for lr in LockableResource.objects.all():
        try:
            lr.release()
        except:
            print(f"Skipping {lr.name}. It is released ...")

    print("All Lockable resources have been released!")
