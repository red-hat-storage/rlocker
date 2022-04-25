from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Get the token for a user"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--user", type=str, required=True)

    def handle(self, *args, **options):
        """
        Retrieve the token for an account
        :return: None
        """
        try:
            existing_user = User.objects.get(username=options.get('user'))
            token = Token.objects.get(user=existing_user).key
            print(token)
        except User.DoesNotExist:
            print(f"User does not exist: {options.get('user')}")
