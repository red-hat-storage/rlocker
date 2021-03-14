import os
from scripts.utils import parse_args
from django.conf import settings


DJANGO_NS = "web"
NGINX_NS = "web"
DB_NS = "db"
class OpenshiftDeployment:
    def __init__(self, api_url=None, token=None):
        '''
        Constructor
        :param api_url:
        :param token:
        '''
        self.api_url = api_url
        self.token = token
        self.django_location = os.path.join(settings.BASE_DIR, "scripts", "deployment", "openshift", DJANGO_NS, 'django')
        self.nginx_location = os.path.join(settings.BASE_DIR, "scripts", "deployment", "openshift", NGINX_NS, 'nginx')
        self.db_location = os.path.join(settings.BASE_DIR, "scripts", "deployment", "openshift", DB_NS)

        self.login()

    def login(self):
        if self.api_url is not None and self.token is not None:
            os.system(f"oc login {self.api_url} --token={self.token}")
        else:
            print("Skipping Login...")

    def create_namespace(self, name):
        os.system(f"oc create namespace {name}")

    def apply(self, path):
        os.system(f"oc apply -f {path}")

    def deploy_django(self):
        self.create_namespace(DJANGO_NS)
        for yaml_file in os.listdir(self.django_location):
            deployment_file = os.path.join(self.django_location, yaml_file)
            self.apply(deployment_file)

    def deploy_nginx(self):
        self.create_namespace(NGINX_NS)
        for yaml_file in os.listdir(self.nginx_location):
            deployment_file = os.path.join(self.nginx_location, yaml_file)
            self.apply(deployment_file)

    def instantiate_db_template(self):
        template_envs_file_location = os.path.join(self.db_location, "instantiate-template.env")
        os.system(f"oc process -f postgresql-persistent --param-file={template_envs_file_location} -n openshift")

    def deploy_db(self):
        self.create_namespace(DB_NS)
        self.instantiate_db_template()


def run(*args):
    '''
    Function that runscript runs when we call a script with python manage.py runscript
    :param args: This comes from the runscript built-in feature.
        We must accept *args as a parameter the way django-extensions designed
    '''
    bool_args, kw_args = parse_args(args)
    deployment = OpenshiftDeployment(kw_args.get('api_url'), kw_args.get('token'))
    if 'django' in bool_args:
        deployment.deploy_django()

    if 'nginx' in bool_args:
        deployment.deploy_nginx()

    if 'db' in bool_args:
        deployment.deploy_db()
