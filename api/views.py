from rest_framework import status
from rest_framework.response import Response
from api.custom_permissions import HasValidTokenOrIsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from lockable_resource.models import LockableResource
from django.db.models.functions import Length
from rqueue.models import Rqueue
from rqueue.constants import Status
from django.shortcuts import  redirect, reverse
from lockable_resource.exceptions import LockWithoutSignoffException
from api.serializers import LockableResourceSerializer, RqueueSerializer
from api.utils import get_user_object_by_token_or_auth
import json


def redirect_to_prior_location(request):
    '''
    We use this only if there is a entry to /api and redirect to somewhere
    :param request:
    :return:
    '''
    return redirect('resources_view')

@api_view(['GET', 'POST'])
@permission_classes([HasValidTokenOrIsAuthenticated])
def resources_view(request):
    '''
    :param request:
    GET:
        Return Response with all LockableResources in a JSON Object,
            instantiating the Serializer class.
        Query Params support:
        label_matches - if request includes `?label_matches=my_label`,
            then it will return a list of the lockable resources,
                that has my_label in its labels_string

    POST:
        Instantiate a LockableResource class and save to the DB.
        Also Instantiate a Serializer class, in order to return JSON
        We create a new dictionary to add more pieces of info to our Response
        Return Response status depending if the request was successful or not.
    '''
    queryset = LockableResource.objects.all()

    if request.method == 'GET':
        #Check if there is label_matches query param
        name = request.query_params.get('name')
        label_matches = request.query_params.get('label_matches')
        free_only = request.query_params.get('free_only')
        signoff = request.query_params.get('signoff')


        if signoff:
            # Here we would like to return immediately, signoff should be unique.
            # And if signoff is not none, then it means it is locked
            # So we should not go over other filtration methods anyway.
            queryset = LockableResource.objects.filter(signoff=signoff)
            serializer = LockableResourceSerializer(queryset, many=True)
            return Response(serializer.data)

        if name and label_matches:
            # Verification that both label and name are not passed in as query param
            return Response(
                'Bad Request! You can not filter both by name and label',
                status=status.HTTP_400_BAD_REQUEST
            )

        # We do not want to convert with bool() here, as it will raise an exception
            # If the value strings are not 'true' or 'false'
        if free_only and free_only.lower() == 'true':
            queryset = queryset.filter(is_locked=False)

        if name is not None:
            # Override the queryset and the serializer to return
            queryset = queryset.filter(name=name)

        if label_matches is not None:
            # Override the queryset and the serializer to return
            # We cant use the built in label_string__contains, as it will retrieve substring
            # For the entire label string, we want to check specific WORDS in label string
            queryset = (x for x in queryset.all() if label_matches in x.labels)
            queryset = sorted(queryset, key=lambda x: len(x.labels))

        serializer = LockableResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        request_data = dict(request.data)
        create_attempt = LockableResource(**request_data)
        serializer = LockableResourceSerializer(create_attempt, data=request_data)

        extended_data = {}
        if serializer.is_valid():
            #Save the serializer, and as well as the changes towards the database via
                # create_attempt.save()
            #We need to copy serializer.data to a new dictionary to add more key values
                #Since the serializer.data is a property, and therefore immutable.
            serializer.save()
            create_attempt.save()
            extended_data['status'] =  'OK'
            extended_data.update(serializer.data)
            return Response(extended_data, status.HTTP_201_CREATED)
        else:
            extended_data['status'] =  'FAILURE'
            extended_data.update(serializer.errors)
            return Response(extended_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([HasValidTokenOrIsAuthenticated])
def resource_view(request, slug):
    '''
    :param request:
    GET:
        Return Response with the requested LockableResources in a JSON Object,
            instantiating the Serializer class.

    PUT:
        Attempt to try to save changes to an existing Lockable Resource object.
        Also Instantiate a Serializer class, in order to return JSON.
        We create a new dictionary to add more pieces of info to our Response.
        We can have certain cases when user attempts to apply changes to an existing
            Lockable Resource
        Return Response depending on the status of the request
    '''
    resource = LockableResource.objects.get(name=slug)

    if request.method == 'GET':
        serializer = LockableResourceSerializer(resource)
        return Response(serializer.data)

    if request.method == 'PUT':
        request_data = dict(request.data)
        serializer = LockableResourceSerializer(resource, data=request_data)
        extended_data = {}
        if serializer.is_valid():
            try:
                #Try saving the changes. This could be both for lock and release
                serializer.save()
                #If no problem with save(), prepare the response:
                extended_data['status'] = 'OK'
                extended_data.update(serializer.data)
                return Response(extended_data, status=status.HTTP_200_OK)

            except LockWithoutSignoffException:
                #We want to handle this exception when it is raised via lockable_resource.signals
                #Prepare a response with bad request:
                return Response({
                    'message': f"Cannot lock resource {resource.name} without signoff. Please provide a signoff!"

                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            #If serializer is not valid because of some reason, we want to prepare a response
                # with the serializer errors
            extended_data['status'] =  'FAILURE'
            extended_data.update(serializer.errors)
            return Response(extended_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([HasValidTokenOrIsAuthenticated])
def retrieve_resource_entrypoint(request, search_string):
    '''
    This view designed to decide where the request should be sent
        right after we identify what is the search_string methodology
    The search string could retrieve a resource by an absolute name of
        a resource
    Or
    It could retrieve a resource by a label that matches the resource

    Therefore, before we enter into queue mechanism, we should first
        check what is the kind of the search_string
    :param request:
    :param search_string: The way to retrieve a resource
    :return: Redirects to view with name or label resource finding
    '''
    request_data = dict(request.data)
    request_signoff = request_data.get('signoff')
    #TODO: Check if the signoff is unique before proceeding to retrieve a resource
    request_priority = int(request_data.get('priority'))
    additional_kwargs = {"priority": request_priority, "signoff": request_signoff}
    try:
        # get() - Throws exception when the filtration does not match
        # Hence, everything has to be wrapped around try catch:
        # See this SO poll: https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
        by_name = LockableResource.objects.get(name=search_string)
        print(f'Search String: {search_string} matches a Lockable resource by name. ID: {by_name.id} \n'
              f'Preparing Request ...')
        by_name_url = reverse(
            'retrieve_resource_by_name',
            kwargs={"name":search_string, **additional_kwargs }
        )
        return redirect(by_name_url)

    except LockableResource.DoesNotExist:
        #If we hit here it means that the requestes resource is not searched by
            # it's name. So we should go ahead and search by a label.
        by_label = search_string in LockableResource.get_all_labels()
        if by_label:
            #This means that we have some resources that are matching a label
                # among all the labels of all resources of the platform
            print(f'Search String: {search_string} is a valid label.  \n'
                  f'Preparing Request ...')
            by_label_url = reverse(
                'retrieve_resource_by_label',
                kwargs={"label": search_string, **additional_kwargs }
            )
            return redirect(by_label_url)
        else:
            return Response({
                'message': f"Search String FAILED in entrypoint. "
                           f"No lockable resource exists that matches this Search String by a name or by a label"

            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([HasValidTokenOrIsAuthenticated])
def retrieve_resource_by_name(request, name, priority, signoff):
    resource = LockableResource.objects.get(name=name)

    # We want to add some more fields to our data before sending it as Request Queue
    custom_data = json.loads(resource.json_parse(override_signoff=True, signoff=signoff))
    custom_data['username'] = get_user_object_by_token_or_auth(request).username
    # Creating the Rqueue and saving it
    put_in_queue = Rqueue(data=json.dumps(custom_data), priority=int(priority))
    put_in_queue.save()

    # After the queue has been created, we'd like to return the response to the svc
        # That handles the queue
    serializer = RqueueSerializer(put_in_queue)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([HasValidTokenOrIsAuthenticated])
def retrieve_resource_by_label(request, label, priority, signoff):
    # The data will be sent to Rqueue without knowing which resource is going to be locked yet.
        # This will be handled by the signals
    custom_data = {
        "label" : label,
        "signoff" : signoff,
        "username" : get_user_object_by_token_or_auth(request).username
    }

    put_in_queue = Rqueue(data=json.dumps(custom_data), priority=int(priority))
    put_in_queue.save()

    # After the queue has been created, we'd like to return the response to the svc
        # That handles the queue
    serializer = RqueueSerializer(put_in_queue)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
def rqueue_view(request, slug):
    '''
    :param request:
    :slug: We will identify the requested Rqueue with it's id
    GET:
        Return Response with the requested Rqueue in a JSON Object

    '''
    rqueue = Rqueue.objects.get(id=slug)
    if request.method == 'GET':
        serializer = RqueueSerializer(rqueue)
        return Response(serializer.data)

    if request.method == 'PUT':
        request_data = dict(request.data)
        serializer = RqueueSerializer(rqueue, data=request_data)
        if serializer.is_valid():
            serializer.save()
            #If no problem with the save(), prepare the response
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def rqueues_view(request):
    '''
    :param request:
    GET:
        Return Response with all the Rqueues in a JSON Object
        Query Params support:
        status - if request includes `?status=my_status`,
            then it will return a list of the queues,
                that it's status is my_status
    '''
    queryset = Rqueue.objects.order_by('-id')

    if request.method == 'GET':
        # Check if status is specified to filter by
        status_matches = request.query_params.get('status')
        if status_matches is not None:
            # Override the queryset and the serializer to return
            # We call upper, the queues status are defined in upper case in: rqueue/constants
            queryset = Rqueue.objects.filter(status=status_matches.upper()).order_by('-id')


        serializer = RqueueSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def rqueues_status_pending_view(request):
    #TODO: Remove this endpoint after making sure that https://www.github.com/jimdevops19/rlockertools.git does not use this endpoint, reason: We can use the rqueues_view with query_param matching
    '''
    :param request:
    GET:
        Return Response with all the Rqueues that are in status Pending
            in a JSON Object
    '''
    rqueue = Rqueue.objects.filter(status=Status.PENDING)

    if request.method == 'GET':
        serializer = RqueueSerializer(rqueue, many=True)
        return Response(serializer.data)