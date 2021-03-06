from urllib.parse import unquote
from django.db.models.signals import pre_save
from django.dispatch import receiver
from lockable_resource.models import LockableResource
from lockable_resource.exceptions import LockWithoutSignoffException
from django.utils import timezone


@receiver(pre_save, sender=LockableResource)
def locking_releasing_verifications_and_actions(sender, instance, **kwargs):
    """
    A signal that runs before saving an object of Lockable Resource
    This signal is to verify whenever user tries to change is_locked=True,
        then there is also a not None value for signoff.
    Otherwise, we don't want to let users to lock resources.
    We also save the time.now() once a resource is locked to track after the time
        that the resource is being locked.
    This signal also ensures that whenever user tries to change is_locked=False,
        it will force the signoff attribute set back to None.
    Since, it does not make sense to have a signoff for a resource we are locking

    :param sender: Lockable Resource model BEFORE the object is changing
    :param instance: Lockable Resource object AFTER the object is changing
    :param kwargs: Must specify for the @receiver decorator

    Tries:
        Check if we can catch the specific object with .get()
    Except DoesNotExist:
        We want to pass, because it means that the object is new
    Else:
        The area we will enter if try block runs successfully,
            and we will take some actions when object tries to be
                locked or released
    """
    try:
        resource = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass

    else:
        if instance.is_locked and not resource.is_locked:  # If resource is locking
            if instance.has_link():
                instance.link = unquote(instance.link)
            if instance.has_signoff():
                print(
                    f"{instance.name} is locking and signoff specified. Saving changes to DB..."
                )
            else:
                raise LockWithoutSignoffException(instance)
            instance.locked_time = timezone.now()

        if not instance.is_locked and resource.is_locked:  # If resource is releasing
            print(
                f"{instance.name} is releasing, setting signoff&link&associated_queue to None before saving changes to DB..."
            )
            instance.signoff = None
            instance.link = None
            instance.associated_queue = None
            instance.locked_time = None
