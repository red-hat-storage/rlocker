from rest_framework import serializers, status, exceptions
from api.serializer_extender import SerializerExtenderManagerByAddon
from lockable_resource.models import LockableResource
from rqueue.models import Rqueue


# Serializer are helper classes to parse the Model objects to JSON objects,
# so we can return Lockable resources object responses via JSON
class LockableResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LockableResource
        fields = "__all__"
        read_only_fields = ["id"]

    # Use this section to add data from addons
    expiry_addon = SerializerExtenderManagerByAddon(
        addon_name="expiry_addon",
        cls_serializer="LockableResourceSerializer",
    )

    def validate(self, attrs):
        """
        Check that the Resource is not Locked
        :param data:
        :return:
        """
        lr_name = attrs.get("name")
        lr_object_pre_save = LockableResource.objects.get(name=lr_name)
        if lr_object_pre_save.is_locked and attrs.get("is_locked"):
            # Important note: raises 406 code status for handling in different services
            raise exceptions.NotAcceptable(
                detail=f"You can not modify a Lockable Resource [{lr_name}] object through the REST API if the resource is locked! "
                "This is prohibited as it might be an attempt locking a resource that is already locked. "
                "Please release first the resource before performing a request that differs from GET. "
            )
        return attrs


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
            "last_beat",
        )
