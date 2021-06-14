from rest_framework import serializers
from lockable_resource.models import LockableResource
from rqueue.models import Rqueue


# Serializer are helper classes to parse the Model objects to JSON objects,
# so we can return Lockable resources object responses via JSON
class LockableResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LockableResource
        fields = "__all__"
        read_only_fields = ["id"]


class RqueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rqueue
        # Here I hardcoded everything, because the ordering is important to display nicer! data is the ugliest display to better it will be last when outputting
        fields = (
            "id",
            "priority",
            "status",
            "time_requested",
            "pending_time",
            "pending_time_descriptive",
            "pended_time_descriptive",
            "description",
            "data",
        )
