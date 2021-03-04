from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'
    def ready(self):
        '''
        We override the ready method of AppConfig, so the application
            could start listening to the signal we create in signals.py
        :return: None
        '''

        import account.signals