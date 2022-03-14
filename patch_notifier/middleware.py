from patch_notifier.models import FirstVisit


class CheckFirstVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to run:
        if request.user.is_authenticated:
            if len(FirstVisit.objects.filter(user=request.user)) == 0 and request.path == '/':
                # It's the user's first visit in index page:
                fv_obj = FirstVisit(
                    user=request.user,
                    is_visited=True
                )
                fv_obj.save()

        return response
