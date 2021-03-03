from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from lockable_resource.models import LockableResource
from lockable_resource.exceptions import LockWithoutSignoffException



@receiver(pre_save, sender=LockableResource)
def locking_releasing_verifications_and_actions(sender, instance, **kwargs):
    '''
    A signal that runs before saving an object of Lockable Resource
    This signal is to verify that whenever user tries to change is_locked=True,
        then there is also a not None value for signoff.
    Otherwise, we don't want to let users to lock resources.
    This signal also ensures that whenever user tries to change is_locked=False,
        it will force the signoff attribute set back to None.
    Since, it does not make sense to have a signoff for a resource we are locking

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    '''
    try:
        resource = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        #If hits except, then object is new, so field hasn't technically changed.
        #In this case we don't want to do anything
        pass

    else:
        #We will enter here only when the try did not fall into except
            #because of non existance
        if instance.is_locked and not resource.is_locked: #If resource is locking
            if instance.has_signoff():
                print(f"{instance.name} is locking and signoff specified. Saving changes to DB...")
            else:
                raise LockWithoutSignoffException(instance)

        if not instance.is_locked and resource.is_locked: #If resource is releasing
            print(f"{instance.name} is releasing, setting signoff to None before saving changes to DB...")
            instance.signoff = None