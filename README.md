# Resource Locker project
## This project is a Back-end service with API endpoints and web UI, for monitoring the resources created in different cloud providers, define their usage availability by locking/unlocking a resource.

### Quick Start Video will be added soon:

Project Architecture:

Django website with applications, `account`, `api`, `dashboard`, `lockable_resource`, `rqueue`
 - __account:__ Designed to add more functionalities to the built-in user app
   - [__ init __](account/__init__.py): Packaging this account directory (Django App) 
   - [apps](account/apps.py): Application configurations 
   - [signals](account/signals.py): A signal to create a Token object so each Account will have an associated Token
   - [urls](account/__urls__.py): Urls that are related to the Account, like user login
   - [views](account/views.py): Views that are related to auth actions like login and logout (We do not enable registration from the WEB UI)

 - __api:__ Application Programming Interface in order to automate resource locking releasing via endpoints.
   - [__ init __](api/__init__.py): Packaging this account directory (Django App) 
   - [apps](api/apps.py): Application configurations 
   - [custom_permissions](api/custom_permissions.py): For enabling only access for non anonymous users, a permission mechanism should be written in api application 
   - [serializers](api/serializers.py): Serializers Object for the api, to prepare JSON responses.
   - [urls](api/__urls__.py): Endpoints that are enabled after the api prefix
   - [views](api/views.py): Views where we will take actions in each endpoint, depending on the request method. 
 
 - __dashboard:__ Designed to display a read-only dashboard for more centralized view of the lockable resources with more details
   - [__ init __](dashboard/__init__.py): Packaging this account directory (Django App) 
   - [apps](dashboard/apps.py): Application configurations 
   - [urls](dashboard/__urls__.py): Endpoints that are enabled for this application
   - [views](dashboard/views.py): Views where we will manipulate the data we'd like to display in the dashboard

 - __lockable_resource:__ Application Programming Interface in order to automate resource locking releasing via endpoints.
   - [__ init __](lockable_resource/__init__.py): Packaging this account directory (Django App) 
   - [admin](lockable_resource/admin.py): Model Registrations to the admin panel of the Django Application 
   - [apps](lockable_resource/apps.py): Application configurations
   - [constants](lockable_resource/constants.py): Constants of the lockable resource app, we define there rules for available status types that a lockable resource object can have
   - [exceptions](lockable_resource/exceptions.py): We define in the exceptions the actions that are not making sense, for i.e locking a resource that is already locked
   - [label_manager](lockable_resource/label_manager.py): Takes responsibility to perform smart retrieving of an available resource by only specifying it's label
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
   - [signals](rqueue/signals.py): Signals to be triggered once a rqueue object is being created, there we handle the queue mechanism.
   - [urls](rqueue/urls.py): Available URL's from the Web UI to manage the requests in queue
   - [utils](rqueue/urls.py): Helper functions for the rqueue applications. for i.e - displaying nicer string for the pended time of a queue
   - [views](rqueue/views.py): Design of the views and actions to take in GET/POST requests.