# Resource Locker project
## This project is a Back-end service with API endpoints and web UI, for monitoring the resources created in different cloud providers, define their usage availability by locking/unlocking a resource.

### Project Dependencies:
 - [rlockerservices](https://github.com/jimdevops19/rlockerservices) - Services repository that the rlocker uses
 - [rlockertools](https://github.com/jimdevops19/rlockertools) -  A Python based client interface to interact with the platform

### Quick Start Video will be added soon

Project Architecture:

Django website with applications, `account`, `api`, `dashboard`, `health`, `lockable_resource`, `rqueue`
 - __account:__ Designed to add more functionalities to the built-in user app
   - [management](account/management/): Directory that includes other python files that could be used as `python manage.py name_of_file` 
   - [__ init __](account/__init__.py): Packaging this account directory (Django App) 
   - [apps](account/apps.py): Application configurations 
   - [signals](account/signals.py): A signal to create a Token object so each Account will have an associated Token
   - [urls](account/__urls__.py): Urls that are related to the Account, like user login
   - [views](account/views.py): Views that are related to auth actions like login and logout (We do not enable registration from the WEB UI)

 - __admin_tools:__ Designed to add more administrative actions, such as importing and exporting the current status of lockable resources
   - [__ init __](admin_tools/__init__.py): Packaging this account directory (Django App) 
   - [apps](admin_tools/apps.py): Application configurations
   - [urls](admin_tools/__urls__.py): Urls that are related to the Admin tools
   - [views](admin_tools/views.py): Views in order to display the different administrative tools

 - __api:__ Application Programming Interface in order to automate resource locking releasing via endpoints.
   - [__ init __](api/__init__.py): Packaging this account directory (Django App) 
   - [apps](api/apps.py): Application configurations 
   - [custom_permissions](api/custom_permissions.py): For enabling only access for non anonymous users, a permission mechanism should be written in api application 
   - [serializers](api/serializers.py): Serializers Object for the api, to prepare JSON responses.
   - [urls](api/urls.py): Endpoints that are enabled after the api prefix
   - [utils](api/utils.py): Useful functions for the api application
   - [views](api/views.py): Views where we will take actions in each endpoint, depending on the request method. 
 
 - __dashboard:__ Designed to display a read-only dashboard for more centralized view of the lockable resources with more details
   - [__ init __](dashboard/__init__.py): Packaging this account directory (Django App) 
   - [apps](dashboard/apps.py): Application configurations 
   - [urls](dashboard/__urls__.py): Endpoints that are enabled for this application
   - [views](dashboard/views.py): Views where we will manipulate the data we'd like to display in the dashboard

 - __health:__ Designed to have a health check URL that returns a raw string, so it will be easier to check health of the entire platform
   - [__ init __](dashboard/__init__.py): Packaging this account directory (Django App) 
   - [apps](dashboard/apps.py): Application configurations 
   - [urls](dashboard/__urls__.py): URL endpoints of this specific application
   - [views](dashboard/views.py): Views of this specific application

 - __lockable_resource:__ Application Programming Interface in order to automate resource locking releasing via endpoints.
   - [__ init __](lockable_resource/__init__.py): Packaging this account directory (Django App) 
   - [management](lockable_resource/management/): Directory that includes other python files that could be used as `python manage.py name_of_file` 
   - [action_manager](lockable_resource/action_manager.py): Includes all the classes that are doing some action on the lockable resource 
   - [admin](lockable_resource/admin.py): Model Registrations to the admin panel of the Django Application 
   - [apps](lockable_resource/apps.py): Application configurations
   - [constants](lockable_resource/constants.py): Constants of the lockable resource app, we define there rules for available status types that a lockable resource object can have
   - [exceptions](lockable_resource/exceptions.py): We define in the exceptions the actions that are not making sense, for i.e locking a resource that is already locked
   - [label_manager](lockable_resource/label_manager.py): Takes responsibility to perform smart retrieving of an available resource by only specifying it's label
   - [query_param_manager](lockable_resource/query_param_manager.py): Includes functions for handling query params in the lockable resource page (for i.e: ?view_as=yaml)
   - [models](lockable_resource/models.py): Modelize a schema of the table for different Lockable resources we will manage.
   - [signals](lockable_resource/signals.py): Signals to be triggered once a specific field of lockable resource object changes
   - [urls](lockable_resource/urls.py): Available URL's from the Web UI to manage the lockable resources
   - [views](lockable_resource/views.py): Design of the views and actions to take in GET/POST requests.
   
 - __rqueue:__ Application for managing the requests that could not be locked immediately, this is a queue management system application
   - [__ init __](rqueue/__init__.py): Packaging this account directory (Django App) 
   - [admin](rqueue/admin.py): Model Registrations to the admin panel of the Django Application 
   - [apps](rqueue/apps.py): Application configurations
   - [constants](rqueue/constants.py): Constants of the rqueue app, we define there priority enumerations, time intervals for resource availability check
   - [context_processors](rqueue/context_processors.py): Since we want some data to be accessible from each HTML template, we have to define it as a global context that is available (from settings.py)
   - [models](rqueue/models.py): Modelize a schema of the table for different requests in queue
   - [signals](rqueue/signals.py): Signals to be triggered once a rqueue object is being created.
   - [urls](rqueue/urls.py): Available URL's from the Web UI to manage the requests in queue
   - [utils](rqueue/urls.py): Helper functions for the rqueue applications. for i.e - displaying nicer string for the pended time of a queue
   - [views](rqueue/views.py): Design of the views and actions to take in GET/POST requests.


# How to use Addons (Plugins) in the Resource Locker Project

## Dev mode:
 - The following are commands to run in your terminal, each line represents a pattern of:   `command to run` __Explanation__
   - `git clone https://github.com/red-hat-storage/rlocker.git` __Clones the project__
   - `cd rlocker` __Change directory__
   - `python --version` __Python3.8 or above is required, please double-check this with that command__
   - `python -m venv venv` __Create a virtual environment for the django app__
   - The following command differs from Windows to Linux systems:
     - `venv\Scripts\activate` __Run this to activate the venv on Windows__
     - `source venv/bin/activate` __Run this to activate the venv on Linux__
   - `pip install -r requirements.txt` __Install the required packages__
     - Expected errors on the command above:
       - `psycopg2-binary==2.8.6 could not be installed`
         - Optional solutions: __(This package could be skipped in dev mode, do not hesitate to comment it out with `#`. The packages will be divided into dev packages and prod packages in the future)__
           - [Helpful SO poll, check out the pre-reqs according to your OS](https://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python)
   - The following commands are environment variable setups. The command to set an env variable is `export` __(PLEASE USE SET AND NOT EXPORT IN WINDOWS!)__
     - Visit the following website in order to generate a secret key for our Django application: [link](https://djecrety.ir/)
       - Click the __Generate__ button to generate a `DJANGO_SECRET`. Now the secret key is copied to your clipboard (Could be pasted the next time you send a Ctrl+V)
       - `export DJANGO_SECRET='<YOUR_COPIED_SECRET>'` Set this env variable. The wrapping with single quotes is important!
       - `export USE_DEV_DB=True` Here we specify to use the local `db.sqlite3` file and not a PostgreSQL database engine (That is why, we could skip the `psycopg2-binary` package in previous steps)
       - `export DEBUG=True` Debug mode on.
   - Launch the website on the desired port (default is 8000)
     - `python manage.py runserver <OPTIONAL_PORT>` As said above, you do NOT HAVE to mention the <OPTIONAL_PORT>
   - Login Credentials are: `admin`, `Admin-1`
 - Next Steps:
   - Visit the [rlockerservices](https://github.com/jimdevops19/rlockerservices) project in order to setup the `queue_service`. 
## Production
 - To be documented