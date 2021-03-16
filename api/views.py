from rest_framework import status
from rest_framework.response import Response
from api.custom_permissions import HasValidToken
from rest_framework.decorators import api_view, permission_classes
from lockable_resource.models import LockableResource
from lockable_resource.label_manager import LabelManager
from django.shortcuts import  redirect
from lockable_resource.exceptions import AlreadyLockedException, LockWithoutSignoffException
from api.serializers import LockableResourceSerializer
import pprint as pp

def redirect_to_prior_location(request):
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

@api_view(['GET'])
@permission_classes([HasValidToken])
def retrieve_resource_view(request, slug):
    '''
    Api View designed to gather one free resource among all the resources,
        We should first check if the given slug is an absolute name of a resource.
        If not, then we should try to find a resource that matches the label, and it is free

    :param request:
    :param slug: Could be the absolute name of the resource or just a label to pick up from
    :return:
    '''
    if request.method == 'GET':
        #First, check if the given slug is an absolute name:
        try:
            #get() - Throws exception when the filtration does not match
            #Hence, everything has to be wrapped around try catch:
            #See this SO poll: https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
            resource = LockableResource.objects.get(name=slug)
            if resource.can_lock:
                #Prepare the Response:
                serializer = LockableResourceSerializer(resource)
                return Response(serializer.data)
            else:
                raise AlreadyLockedException


        except LockableResource.DoesNotExist:
            #We;d only like to print this in the background, because maybe the given slug
                #is actually a label.
            print(f"Could not find a free resource by it's name: {slug}."
                  "Searching based on resources labels.")

        except AlreadyLockedException:
            return Response({
                'message' : 'The requested resource matched to an existing name, but it is locked'
            },status=status.HTTP_206_PARTIAL_CONTENT)


        #If no resource found by filtering with name, we'll try to find a matching label
        resource_by_label = LabelManager(label=slug)
        resource = resource_by_label.retrieve_free_resource()
        if resource:
            serializer = LockableResourceSerializer(resource)
            return Response(serializer.data)

        else:
            return Response({
                'message' : 'There are no free resources that matches the given name or label'
            },status=status.HTTP_206_PARTIAL_CONTENT)