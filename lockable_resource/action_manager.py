# This file is in order to manage different actions for each lockable resources
# We also want to be able to return the desired actions for the possible addons

# Conventions for shortening class names:
# LR -> Lockable Resource


import lockable_resource.constants as const
import rqueue.constants as const_rqueue
from abc import abstractmethod
from django.http import HttpRequest
from django.contrib import messages
from lockable_resource.models import LockableResource
from rqueue.models import Rqueue
from rqueue.constants import Priority


# CHANGE THIS COMMENT SECTION IF THE LOGIC OF THIS FILE IS MODIFIED!
# How to add an action ?
# Add it to SUPPORTED_ACTIONS (Better to first create a constant of it like the existings)
# Implement a new subclass of LRActionManager
# In the SUPPORTED_ACTIONS_OBJECTS<LRActionObjectsHandler>, add a new key&value pair that returns an instance of the relevant subclass

# This list is not inside the constants.py, since it might be extended by addons
SUPPORTED_ACTIONS = [
    const.ACTION_LOCK,
    const.ACTION_RELEASE,
    const.ACTION_MAINTENANCE_MODE_ENTER,
    const.ACTION_MAINTENANCE_MODE_EXIT,
]


class LRActionManager:
    def __init__(self, request: HttpRequest, **kwargs):
        """
        Initialization.
        :param
        :param request: The Django request
        :param kwargs: Additional key-worded args received

        Keep the validations() the last line in the init method,
            so that it will run after the objects are assigned!
        """
        self.request = request
        self.kwargs = kwargs

        # Useful attributes:
        self.action = request.POST.get("action")  # get action
        self.r_lock_id = int(request.POST.get("id"))  # get ID of lockable resource
        self.r_lock_obj = LockableResource.objects.get(
            id=self.r_lock_id
        )  # get object of lockable resource

        self.validations()

    def validations(self):
        """
        Add here validations for the received args in init
        """
        assert (
            self.action in SUPPORTED_ACTIONS
        ), f"Action {self.action} not in {SUPPORTED_ACTIONS}"

    @abstractmethod
    def complete_action(self):
        pass


class LRActionLock(LRActionManager):
    def complete_action(self):
        signoff = self.request.POST.get(f"signoff-{self.r_lock_id}")  # get signoff
        # Create a queue for this lock request with priority 0
        new_queue = Rqueue(
            priority=Priority.UI.value,
            data=self.r_lock_obj.json_parse(
                # We'd like to parse a new json with the requested signoff from the POST request
                override_signoff=True,
                signoff=signoff,
            ),
            status=const_rqueue.Status.INITIALIZING,
        )
        new_queue.save()
        messages.info(
            self.request,
            message=f"{self.r_lock_obj.name} has been sent to Pending requests"
            f" with Priority {new_queue.priority}! Signoff: {signoff}",
        )


class LRActionRelease(LRActionManager):
    def complete_action(self):
        self.r_lock_obj.release()
        messages.info(
            self.request,
            message=f"{self.r_lock_obj.name} has been released successfully!",
        )


class LRActionEnterMaintenance(LRActionManager):
    def complete_action(self):
        self.r_lock_obj.in_maintenance = True
        self.r_lock_obj.save()
        messages.info(
            self.request,
            message=f"{self.r_lock_obj.name} has been Entered to Maintenance Mode!",
        )


class LRActionExitMaintenance(LRActionManager):
    def complete_action(self):
        self.r_lock_obj.in_maintenance = False
        self.r_lock_obj.save()
        messages.info(
            self.request,
            message=f"{self.r_lock_obj.name} has been Exited from Maintenance Mode! Resources now could be locked/released as usual!",
        )


class LRActionObjectsHandler(LRActionManager):
    def get_supported_actions_objects(self):
        """
        A method to return the wanted instance of LR Action
        TODO: Possibly find a way to refer to request obj without passing it
            separately to each one of the LRAction implementations ?
        """

        SUPPORTED_ACTIONS_OBJECTS = {
            const.ACTION_LOCK: LRActionLock(self.request),
            const.ACTION_RELEASE: LRActionRelease(self.request),
            const.ACTION_MAINTENANCE_MODE_ENTER: LRActionEnterMaintenance(self.request),
            const.ACTION_MAINTENANCE_MODE_EXIT: LRActionExitMaintenance(self.request),
        }

        return SUPPORTED_ACTIONS_OBJECTS

    def get_desired_action_instance(self):
        return self.get_supported_actions_objects().get(self.action)
