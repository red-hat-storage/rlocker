import os
from scripts.utils import parse_args

DJANGO_NS = "web"
NGINX_NS = "web"
DB_NS = "db"
class OpenshiftDeployment:
    def __init__(self, api_url, token, skip_db=True, skip_nginx=True, skip_django=True):
        '''
        Constructor
        :param api_url:
        :param token:
        :param skip_db:
        :param skip_nginx:
        :param skip_django:
        '''
        self.api_url = api_url
        self.token = token
        self.skip_db = skip_db
        self.skip_nginx = skip_nginx
        self.skip_django = skip_django

        self.django_location = os.path.join(os.curdir, "deployment", "openshift", DJANGO_NS, 'django')
        self.nginx_location = os.path.join(os.curdir, "deployment", "openshift", NGINX_NS, 'nginx')
        self.db_location = os.path.join(os.curdir, "deployment", "openshift", DB_NS)

        self.login()

    def login(self):
        os.system(f"oc login {self.api_url} --token={self.token}")

    def create_namespace(self, name):
        os.system(f"oc create namespace {name}")

    def apply(self, path):
        os.system(f"oc apply -f {path}")

    def deploy_django(self):
        self.create_namespace(DJANGO_NS)
        for yaml_file in os.listdir(self.django_location):
            deployment_file = os.path.join(self.django_location, yaml_file)
            self.apply(deployment_file)




def run(*args):
    '''
    Function that runscript runs when we call a script with python manage.py runscript
    :param args: This comes from the runscript built-in feature.
        We must accept *args as a parameter the way django-extensions designed
    '''
    bool_args, kw_args = parse_args(args)
    deployment = OpenshiftDeployment(kw_args.get('api_url'), kw_args.get('token'))
    deployment.deploy_django()



