from lockable_resource.models import LockableResource


class QueryParamManager:
    SUPPORTED_QUERY_PARAMS=[
        'view_as'
    ]

    def __new__(cls, key, value):
        '''
        Do not create an instance if key not in supported query params
        :param key:
        :return Query Params object:
        '''
        if not key in cls.SUPPORTED_QUERY_PARAMS:
            # no rows, so no data. Return `None`.
            return None

        # create a new instance and set attributes on it
        instance = super().__new__(cls)  # empty instance
        instance.key = key
        instance.value = value
        return instance

    def handle_key(self):
        if self.key == 'view_as':
            if self.value == 'yaml':
                return LockableResource.get_objects_as_yaml()