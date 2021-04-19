#This file is to write more permission rather than what django rest frame has to offer
from rest_framework.permissions import BasePermission

from api.utils import get_auth_token_header, token_exists


class HasValidToken(BasePermission):
    """
    Allow access if the token is valid.
    """
    def has_permission(self, request, view):
        auth_token_header = get_auth_token_header(request)
        if auth_token_header:
            #Response returns tuple, we should grab the provided token string
            key, token_string = auth_token_header
            token = token_string.replace('Token ' , '')
            return token_exists(token)

class HasValidTokenOrIsAuthenticated(BasePermission):
    """
    Allow access if the token is valid OR if the user is authenticated
    The reason we do this, it is because we'd like to allow permissions if the user
        is authenticated (UI access) or if the user provided an existing token
    """
    def has_permission(self, request, view):
        auth_token_header = get_auth_token_header(request)
        token=None
        if auth_token_header:
            #Response returns tuple, we should grab the provided token string
            key, token_string = auth_token_header
            token = token_string.replace('Token ' , '')
            # We want to return whether if token exists, or the user is authenticated,
                # The statement in () taken from the return value of IsAuthenticated built-in permission class
        return \
            token_exists(token) or (bool(request.user and request.user.is_authenticated))