from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_token_once_user_registers(sender, instance, created, **kwargs):
    '''
    A signal that runs after a user is registered to our system
    This signal is to verify whenever user is registered, he will also receive
        a token to create API requests

    :param sender: User model BEFORE the object is created
    :param instance: User object AFTER the object is created
    :param created: Django uses save() method both when object is created or changed,
        so this param will allow identifying if object is created.
    :param kwargs: Must specify for the @receiver decorator
    '''
    if created:
        Token.objects.create(user=User.objects.get(username=instance.username))
        print(f'Token Generated for user:{instance.username}')