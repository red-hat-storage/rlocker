from django.db import models
from lockable_resource.exceptions import AlreadyFreeException, AlreadyLockedException
import lockable_resource.constants as const
import json

class LockableResource(models.Model):
    #Fields:
        # id - Primary key to identify each lockable resource obj. (Auto Generated)
        # provider - The Cloud provider.
        # name - Name of the resource.
        # is_locked - Status of the lockable resource described by
        #    if locked or not, default is False. New created Lockable
        #       resource should be released.
        # labels - All the labels a lockable resource can have.
        # signoff - To be aware who locked the resource, we want to have a signoff
        #               that will describe who was in charge to change the status of it.

    provider = models.CharField(max_length=256)
    name =  models.CharField(max_length=256, unique=True)
    is_locked = models.BooleanField(default=False)
    labels_string = models.CharField(max_length=2048)
    signoff = models.CharField(max_length=2048, null=True, default=None, blank=True)

    @property
    def labels(self):
        '''
        Instance Property
        Since the labels are stored as white-space separated in DB,
            this property is to receive the labels as a list
        :returns: List of all the labels
        '''
        return self.labels_string.split()

    @property
    def status_properties(self):
        '''
        Instance Property
        Includes additional key&values about the status of the LockableResource obj
        Depending on the status, we want to include different styling for the HTML template

        :returns: Dictionary:
            `status` : Status of the LR, locked or not
            `color`  : Color to describe the situation (Green or Red)
            `icon`  : Icon to describe the situation from Bootstrap Classes
        '''
        if self.is_locked:
            return {'status' : const.STATUS_LOCKED, 'color': '#D6212E', 'icon' : 'icon_lock'}
        else:
            return {'status' : const.STATUS_FREE, 'color': '#00C100', 'icon' : 'icon_lock-open' }

    @property
    def can_lock(self):
        '''
        Instance Property
        :returns Boolean:
        '''
        return not self.is_locked

    @property
    def can_release(self):
        '''
        Instance Property
        :returns Boolean:
        '''
        return self.is_locked

    def lock(self, signoff):
        '''
        Instance Method

        :param signoff: The message to describe who locks the resource
        This method will lock the resource if it is requested.
            It will assign a new signoff message.

        :raises: AlreadyLockedException
        :returns: None
        '''
        if self.can_lock:
            self.is_locked = True
            self.signoff = signoff
            self.save()
        else:
            raise AlreadyLockedException()

    def release(self):
        '''
        Instance Method

        This method will release the resource if it is requested.
            Will reset the attribute if signoff to None.

        :raises: AlreadyFreeException
        :returns: None
        '''
        if self.can_release:
            self.is_locked = False
            self.delete_signoff()
            self.save()
        else:
            raise AlreadyFreeException()

    def delete_signoff(self):
        '''
        Instance Method
        :returns: None
        '''
        self.signoff = None

    def has_label(self, label):
        return label in self.labels

    def has_signoff(self):
        return self.signoff is not None

    @staticmethod
    def get_all_free_resources():
        return LockableResource.objects.filter(is_locked=False)

    def __str__(self):
        '''
        Instance Magic Method __str__
        This will make the object more descriptive.
        Helpful in the Admin page
        '''
        return self.name

    @staticmethod
    def get_all_labels():
        '''
        Static Method
        Responsible to return a non-duplicated list of ALL the labels
            of the entire platform
        :return:
        '''
        all_labels = []
        for lockable_resource in LockableResource.objects.all():
            for label in lockable_resource.labels:
                all_labels.append(label)

        #Lets remove duplicates by converting to a set:
        all_labels = set(all_labels)

        #Now revert this back to list:
        all_labels = list(all_labels)

        return all_labels


    def json_parse(self, **kwargs):
        '''
        Instance Method
        Method prepares the object in parsed json.
        We want to omit several key values from the
        built-in __dict__ attribute, to have cleaner data
        Removals are in list: key_removals
        :return: JSON object
        '''
        key_removals = ['labels_string','_state']
        obj_dict = self.__dict__
        for key_removal in key_removals:
            #Try to remove the key SILENTLY:
            obj_dict.pop(key_removal, None)

        if kwargs.get('override_signoff'):
            obj_dict['signoff'] = kwargs.get('signoff')

        return json.dumps(obj_dict)


    # Meta Class
    class Meta:
        #Override verbose name plural to get nicer description in Admin Page:
        verbose_name_plural = "Lockable Resources"
