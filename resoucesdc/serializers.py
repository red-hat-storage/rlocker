from rest_framework import serializers
from .models import ResoucesDC

class ResourcesDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResoucesDC
        fields = ('id', 'dc', 'storage', 'cpu', 'memory', 'usedstorage', 'usedcpu', 'usedmemory')
        