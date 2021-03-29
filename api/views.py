from rest_framework import status
from rest_framework.response import Response
from api.custom_permissions import HasValidToken
from rest_framework.decorators import api_view, permission_classes
from lockable_resource.models import LockableResource
from rqueue.models import Rqueue, FinishedQueue
from lockable_resource.label_manager import LabelManager
from django.shortcuts import  redirect, HttpResponseRedirect, reverse
from lockable_resource.exceptions import AlreadyLockedException, LockWithoutSignoffException
from api.serializers import LockableResourceSerializer, RqueueSerializer
import json
def redirect_to_prior_location(request):
    '''
    We use this only if there is a entry to /api and redirect to somewhere
    :param request:
    :return:
    '''
    return redirect('resources_view')

@api_view(['GET', 'POST'])
@permission_classes([HasValidToken])
def resources_view(request):
    '''
    :param request:
    GET:
        Return Response with all LockableResources in a JSON Object,
            instantiating the Serializer class.

    POST:
        Instantiate a LockableResource class and save to the DB.
        Also Instantiate a Serializer class, in order to return JSON
        We create a new dictionary to add more pieces of info to our Response
        Return Response status depending if the request was successful or not.
    '''
    all = LockableResource.objects.all()

    if request.method == 'GET':
        serializer = LockableResourceSerializer(all, many=True)
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
@permission_classes([HasValidToken])
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
@permission_classes([HasValidToken])
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
@permission_classes([HasValidToken])
def retrieve_resource_by_name(request, name, priority, signoff):
    resource = LockableResource.objects.get(name=name)
    #We should get the priority and convert this to int
    put_in_queue = Rqueue(data=resource.json_parse(override_signoff=True, signoff=signoff), priority=int(priority))
    put_in_queue.save()
    #If we got pass this line, it means the queue has done it's job
    #And we can return success message
    #Bring the latest Finished Queue
    return Response({
        #We'd like to return response that the request has been completed and moved to
            # Finished Queue.
        #Since we immediately store the info of Rqueue in FinishedQueue, then we can use .last()
        #For the FinishedQueue objects
        'message': f"{name} has been locked!",
        'waited_time' : FinishedQueue.objects.last().pended_time_descriptive

    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([HasValidToken])
def retrieve_resource_by_label(request, label, priority, signoff):
    # The data will be sent to Rqueue without knowing which resource is going to be locked yet.
        # This will be handled by the signals
    custom_data = {
        "search_string" : label,
        "signoff" : signoff,
    }

    put_in_queue = Rqueue(data=json.dumps(custom_data), priority=int(priority))
    put_in_queue.save()

    #TODO: We should be aware what resource was locked
    #Additional logs about which specific resource really locked will the throwen by the signal itself

    return Response({
        #We'd like to return response that the request has been completed and moved to
            # Finished Queue.
        #Since we immediately store the info of Rqueue in FinishedQueue, then we can use .last()
        #For the FinishedQueue objects
        'message': f"Resource with label {label} has been locked!",
        'waited_time' : FinishedQueue.objects.last().pended_time_descriptive

    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def pendingrequest_view(request, slug):
    '''
    :param request:
    :slug: We will identify the requested Rqueue with it's id
    GET:
        Return Response with the requested Rqueue in a JSON Object

    '''
    try:
        rqueue = Rqueue.objects.get(id=slug)
        serializer = RqueueSerializer(rqueue)
        return Response(serializer.data)
    except:
        return Response(None)

@api_view(['GET'])
def pendingrequests_view(request):
    '''
    :param request:
    GET:
        Return Response with all the Rqueues in a JSON Object
    '''
    rqueue = Rqueue.objects.all()

    if request.method == 'GET':
        serializer = RqueueSerializer(rqueue, many=True)
        return Response(serializer.data)