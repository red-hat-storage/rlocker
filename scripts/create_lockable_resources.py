from lockable_resource.models import LockableResource
from pathlib import Path
import yaml
import os


def run():
    """
    Function inserts the lockable resources based on what is existing in the YAML file
        If Lockable resource is already created, then it will not create it

    :return:
    """
    YAML_FILE = os.path.join(Path(__file__).parent, "data", "lockableresources.yaml")
    with open(YAML_FILE, "r") as f:
        resources_object = yaml.safe_load(f.read())

    for lr in resources_object["lockable_resources"]:
        lr_name = lr.get("name")
        if len(LockableResource.objects.filter(name=lr_name)) == 0:
            lr_obj = LockableResource(**lr)
            lr_obj.save()
            print(f"{lr_obj.name} added!")
        else:
            print(f"{lr_name} exists! Continuing...")
            continue
