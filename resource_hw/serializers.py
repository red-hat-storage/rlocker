from rest_framework import serializers
from .models import ResouceHW

class ResourceHWSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResouceHW
        fields = ('id', 'dc_name', 'storage_max', 'cpu_max', 'memory_max', 'storage_used', 'cpu_used', 'memory_used')
