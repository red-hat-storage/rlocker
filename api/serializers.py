from rest_framework import serializers
from lockable_resource.models import LockableResource


#Serializer are helper classes to parse the Model objects to JSON objects,
    #so we can return Lockable resources object responses via JSON
class LockableResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LockableResource
        fields = '__all__'
        read_only_fields = ['id']