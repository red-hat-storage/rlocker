# Global context processors declared
# Therefore, we could access the values (by referring to their keys)
# using the jinja syntax from ALL the HTML templates

from django.conf import settings


def global_context_processors(request):
    return {
        "installed_addons" : settings.INSTALLED_ADDONS
    }
