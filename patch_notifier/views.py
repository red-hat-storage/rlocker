from patch_notifier.models import FirstVisit
from django.shortcuts import redirect


def update_first_visit(request):
    '''
    This function is used when a user clicks on "Do not read this anymore"
    So we will have the option to handle a post request here, only!
    :param request:
    :return:
    '''
    if request.method == 'POST' and request.user.is_authenticated:
        if len(FirstVisit.objects.filter(user=request.user)) == 0:
            fv_obj = FirstVisit(
                user=request.user,
                is_visited=True
            )
            fv_obj.save()

        return redirect('dashboard_page')
