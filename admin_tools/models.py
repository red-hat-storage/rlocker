from django.db import models
import admin_tools.constants as const
import yaml


class Addon(models.Model):
    package_name = models.CharField(
        max_length=64,
        unique=True,
    )
    application_name = models.CharField(
        max_length=64,
        unique=True,
    )
    package_url = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        default=None,
        unique=True,
    )
    project_url = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        default=None,
        unique=True,
    )
    is_installed = models.BooleanField(default=False)

    def __str__(self):
        return self.package_name

    @staticmethod
    def insert_supported_addons():
        """
        Static method that reads the yaml file of supported addons.
        Inserts them to the DB inside this Model
        """
        with open(const.SUPPORTED_ADDONS_FILE, "r") as f:
            addons = yaml.safe_load(f.read()).get("addons")
        for addon in addons:
            addon_package_name = addon.get("package_name")
            try:
                Addon.objects.get(package_name=addon_package_name)
            except Addon.DoesNotExist:
                addon_obj = Addon(**addon)
                addon_obj.save()
                print(f"Added: {addon_obj}!")

    @staticmethod
    def get_installed_addons(key=None):
        """
        Build a queryset on installed addons
        :param key: If provided, will build a list of all the fields
        """
        installed_addons = Addon.objects.filter(is_installed=True)
        if not key:
            return installed_addons
        else:
            return list(installed_addons.values_list(key, flat=True))
