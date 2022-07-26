# File is used to check if more data needs to be added to the current serializers because of addons
from django.conf import settings
import inspect
import importlib

# TODO: Possibly find a more generic way adding data to serializers.
# This way, not every addon developer needs to go through editing the api/serializers.py


class SerializerExtenderManagerByAddon:
    def __new__(cls, addon_name, cls_serializer):
        """
        Do not create an instance if the addon not in settings.INSTALLED_ADDONS
        :param key:
        :return Query Params object:
        """
        if not addon_name in settings.INSTALLED_ADDONS:
            # TODO: Consider throwing an exception here
            return None

        # create a new instance and set attributes on it
        instance = super().__new__(cls)  # empty instance
        instance.addon_name = addon_name
        instance.cls_serializer = cls_serializer
        return instance.get_serializer()

    def get_source_adder(self):
        """
        Method that checks the existing classes in the serializers module
            and returns the SourceAdder

        """
        serializers_addon = importlib.import_module(f"{self.addon_name}.serializers")
        cls_members = inspect.getmembers(serializers_addon, inspect.isclass)
        for cls in cls_members:
            if cls[0].endswith("SourceAdder"):
                return cls[1]

    def get_serializer(self):
        """
        Retrieves the serializer from serializers module within the addon
        It is important to follow the following conventions in order to successfully use your data
            inside the addon
        - Module name should be serializers.py
        - Should use a class with the convention of <ModelName>SourceAdder
        - Include the fields:
            - extend_serializer (str)
            - serializer (cls)
            - read_only (bool)
            - source (str)
        Use the expiry_addon (the first addon created for rlocker) as a reference for example
        """
        # Naming the following variable by purpose with this syntax
        # Since, get_source_adder should be a function that returns a reference to a class
        SourceAdderCls = self.get_source_adder()

        # Check that the SourceAdderCls has extend_serializer attribute
        if SourceAdderCls.__dict__.get("extend_serializer"):
            if SourceAdderCls.extend_serializer == self.cls_serializer:
                return SourceAdderCls.serializer(
                    read_only=SourceAdderCls.read_only, source=SourceAdderCls.source
                )
        else:
            raise Exception(
                f"Bad Implementation of the class {SourceAdderCls}. "
                "Missing key extend_serializer that should be storing a value of the Serializer class name "
                "that you wish to add the data to."
            )
