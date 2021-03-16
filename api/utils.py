from django.contrib.auth.models import User
#Utilities for API Application


def get_auth_token_header(request):
    '''
    The token that is going to be provided is going to be stored within
        this area of the request
    :param request:
    :return:
    '''
    return request.headers._store.get('authorization')


def token_exists(token_to_validate):
    try:
        User.objects.get(auth_token=token_to_validate)
        return True
    except:
        return False