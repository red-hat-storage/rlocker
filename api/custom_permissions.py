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

