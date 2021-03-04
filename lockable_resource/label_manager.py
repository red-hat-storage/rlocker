#This file will include filtration functionalities based on resource labels
from lockable_resource.models import LockableResource
from lockable_resource.exceptions import FreeResourceNotAvailableException


class LabelManager:
    def __init__(self, label):
        '''
        constructor
        :param label: for the filtration, we receive one param as the
            wanted label
        all_free_resources - gather all the Lockable resource objects that
            could be locked (Not filtered by a label)
        '''
        self.all_free_resources = LockableResource.get_all_free_resources()
        self.label = label

    def get_free_resources(self):
        '''
        Instance Method
        Filtration to receive all free resources that are matching the
            given label when the class is instantiated
        :return: List of all free resources that matches the label
        '''
        matching_resources = []
        for resource in self.all_free_resources:
            if resource.has_label(self.label):
                matching_resources.append(resource)

        return matching_resources

    def prioritize_resources(self):
        '''
        Instance Method
        Sorting to have the free resources sorted by the amount of labels
        We know that the more labels a resource has, the more rare the cases
            that we'd like to lock it.
        Hence, we sort by the length of the labels list
        :return: List (Sorted)
        '''
        lambda_prioritize = lambda x: len(x.labels)
        resources_prioritized = self.get_free_resources()
        resources_prioritized.sort(key=lambda_prioritize)
        return resources_prioritized

    def retrieve_free_resource(self, not_exist_ok=True):
        '''
        Attempts to retrieve free resource with the instantiated label
        :param: not_exist_ok(default: True) - Not always we'd like to throw exception,
            If no free resource could be retrieved
        Tries:
            To catch the first index of prioritized resources.
            Since we prioritize from low to high, then it is Ok to attempt
                indexing zero.
            :return: LockableResource object
        Raises:
            FreeResourceNotAvailableException - If there is an IndexError
                when we attempt to index zero, it means the prioritize was
                    empty from the beginning.
            Therefore, we raise this exception
        '''
        try:
            retrieved_resource = self.prioritize_resources()[0]
            return retrieved_resource

        except IndexError:
            if not_exist_ok:
                return None
            else:
                raise FreeResourceNotAvailableException(self.label)