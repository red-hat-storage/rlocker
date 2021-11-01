from django.db import models
from lockable_resource.exceptions import AlreadyFreeException, AlreadyLockedException
import lockable_resource.constants as const
import json
import yaml


class LockableResource(models.Model):
    # Fields:
    # id - Primary key to identify each lockable resource obj. (Auto Generated)
    # provider - The Cloud provider.
    # name - Name of the resource.
    # is_locked - Status of the lockable resource described by
    #    if locked or not, default is False. New created Lockable
    #       resource should be released.
    # labels - All the labels a lockable resource can have.
    # signoff - To be aware who locked the resource, we want to have a signoff
    #               that will describe who was in charge to change the status of it.
    # TODO: signoff should support HTML so it will be easier to send Jenkins Job Links
    # description - We want to have some random text to describe lockable resource
    # in_maintenance - Describes whether if the resource is in maintenance or not, we will disable
    # all functionalities to lock/release resource is it is.

    provider = models.CharField(max_length=256)
    name = models.CharField(max_length=256, unique=True)
    is_locked = models.BooleanField(default=False)
    labels_string = models.CharField(max_length=2048)
    signoff = models.CharField(
        max_length=2048, null=True, default=None, blank=True, unique=True
    )
    description = models.CharField(max_length=2048, null=True, default=None, blank=True)
    link = models.CharField(max_length=2048, null=True, default=None, blank=True)
    in_maintenance = models.BooleanField(default=False)

    @property
    def labels(self):
        """
        Instance Property
        Since the labels are stored as white-space separated in DB,
            this property is to receive the labels as a list
        :returns: List of all the labels
        """
        return self.labels_string.split()

    @property
    def free_and_not_in_maintenance(self):
        """
        Instance Property
        Returns if the lockable resource could be locked at all.
             - Resource could be locked
             - Resource could be under maintenance


        :return: Bool True/False
        """
        return not self.is_locked and not self.in_maintenance

    @property
    def status_properties(self):
        """
        Instance Property
        Includes additional key&values about the status of the LockableResource obj
        Depending on the status, we want to include different styling for the HTML template

        :returns: Dictionary:
            `status` : Status of the LR, locked or not
            `color`  : Color to describe the situation (Green or Red)
            `icon`  : Icon to describe the situation from Bootstrap Classes
        """
        if self.is_locked:
            return {
                "status": const.STATUS_LOCKED,
                "color": "#D6212E",
                "icon": "icon_lock",
            }
        else:
            return {
                "status": const.STATUS_FREE,
                "color": "#00C100",
                "icon": "icon_lock-open",
            }

    @property
    def can_lock(self):
        """
        Instance Property
        :returns Boolean:
        """
        return not self.is_locked

    @property
    def can_release(self):
        """
        Instance Property
        :returns Boolean:
        """
        return self.is_locked

    def lock(self, signoff):
        """
        Instance Method

        :param signoff: The message to describe who locks the resource
        This method will lock the resource if it is requested.
            It will assign a new signoff message.

        :raises: AlreadyLockedException
        :returns: None
        """
        if self.can_lock:
            self.is_locked = True
            self.signoff = signoff
            self.save()
        else:
            raise AlreadyLockedException()

    def release(self):
        """
        Instance Method

        This method will release the resource if it is requested.
            Will reset the attribute if signoff to None.

        :raises: AlreadyFreeException
        :returns: None
        """
        if self.can_release:
            self.is_locked = False
            self.delete_signoff()
            self.save()
        else:
            raise AlreadyFreeException()

    def delete_signoff(self):
        """
        Instance Method
        :returns: None
        """
        self.signoff = None

    def has_label(self, label):
        return label in self.labels

    def has_link(self):
        # Sometimes the link might be stringed none.
        # We want to ensure that it is not the case as well
        return self.link not in [None, "None"]

    def has_signoff(self):
        return self.signoff is not None

    @staticmethod
    def get_all_free_resources(ignore_maintenance=False):
        if ignore_maintenance:
            return LockableResource.objects.filter(is_locked=False)
        else:
            return LockableResource.objects.filter(
                is_locked=False, in_maintenance=False
            )

    def __str__(self):
        """
        Instance Magic Method __str__
        This will make the object more descriptive.
        Helpful in the Admin page
        """
        return self.name

    @staticmethod
    def get_all_labels():
        """
        Static Method
        Responsible to return a non-duplicated list of ALL the labels
            of the entire platform
        :return:
        """
        all_labels = []
        for lockable_resource in LockableResource.objects.all():
            for label in lockable_resource.labels:
                all_labels.append(label)

        # Lets remove duplicates by converting to a set:
        all_labels = set(all_labels)

        # Now revert this back to list:
        all_labels = list(all_labels)

        return all_labels

    def json_parse(self, **kwargs):
        """
        Instance Method
        Method prepares the object in parsed json.
        We want to omit several key values from the
        built-in __dict__ attribute, to have cleaner data
        Removals are in list: key_removals
        :return: JSON object
        """
        key_removals = ["_state", "in_maintenance", "is_locked"]
        obj_dict = self.__dict__
        for key_removal in key_removals:
            # Try to remove the key SILENTLY:
            obj_dict.pop(key_removal, None)

        if kwargs.get("override_signoff"):
            obj_dict["signoff"] = kwargs.get("signoff")

        if kwargs.get("override_link"):
            obj_dict["link"] = kwargs.get("link")

        return json.dumps(obj_dict)

    def yaml_parse(self):
        """
        Instance Method
        Method prepares the object in parsed yaml.
        We want to omit several key values from the
        built-in __dict__ attribute, to have cleaner data
        Removals are in list: key_removals
        :return: YAML object
        """
        key_removals = ["_state", "id"]
        obj_dict = self.__dict__
        for key_removal in key_removals:
            # Try to remove the key SILENTLY:
            obj_dict.pop(key_removal, None)

        return yaml.safe_dump(obj_dict)

    @classmethod
    def get_objects_as_yaml(cls):
        '''
        Returns all the objects as YAML
        :return:
        '''
        indent = ' ' * 2
        raw_yaml = ''
        raw_yaml += '---\n'
        raw_yaml += 'lockable_resources:\n'
        for obj in cls.objects.all():
            raw_yaml += f"{indent}-\n"
            for line in obj.yaml_parse().split('\n'):
                raw_yaml += f"{indent}{indent}{line}\n"

        return raw_yaml



    # Meta Class
    class Meta:
        # Override verbose name plural to get nicer description in Admin Page:
        verbose_name_plural = "Lockable Resources"
