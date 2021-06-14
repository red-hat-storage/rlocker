from django.contrib.auth.models import User

# Utilities for API Application


def get_auth_token_header(request):
    """
    The token that is going to be provided is going to be stored within
        this area of the request
    :param request:
    :return:
    """
    return request.headers._store.get("authorization")


def token_exists(token_to_validate):
    """
    Returns if the token exists or not
    :param token_to_validate:
    :return: bool
    """
    try:
        User.objects.get(auth_token=token_to_validate)
        return True
    except:
        return False


def get_user_object_by_token(request):
    # Token Header tuple, we should grab the provided token string
    key, token_string = get_auth_token_header(request)
    token = token_string.replace("Token ", "")
    user_obj = User.objects.get(auth_token=token)
    return user_obj


def get_user_object_by_token_or_auth(request):
    """
    We'd like to have a function that will check try to return the user object
        by auth or by a token.
    Currently, not handling the API request cases without a token and without and auth
    :param request:
    :return:
    """
    try:
        return get_user_object_by_token(request)
    except:
        return request.user
