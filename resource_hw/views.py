from django.shortcuts import render
from rest_framework import viewsets
from .models import ResouceHW
from .serializers import ResourceHWSerializer

#viewsets provides the base classes for creating API views that perform CRUD 
# (Create, Read, Update, Delete) operations on your data models.
class ResourceHWView(viewsets.ModelViewSet):
    # creating a queryset for the Django model named Course. 
    # This line of code is a common way to retrieve all records 
    # from the database associated with the Course model.
    queryset = ResouceHW.objects.all()
    # This is an attribute you set in a DRF view or viewset to specify which 
    # serializer class should be used for serializing and deserializing data when processing HTTP requests.
    serializer_class = ResourceHWSerializer