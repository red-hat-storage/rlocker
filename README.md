# Resource Locker project
## This project is a Back-end service with endpoints and web UI, for monitoring the resources created in different cloud providers

### Quick Start:

Project Architecture:

Django website with applications, `account`,`api`,`lockable_resource`
 - __account:__ Designed to add more functionalities to the built-in user app.
   - [__ init __](account/__init__.py): Packaging this account directory (Django App) 
   - [apps](account/apps.py): Application configurations 
   - [signals](account/signals.py): A signal to create a Token object so each Account will have an associated Token.
   - [urls](account/__urls__.py): Urls that are related to the Account, like user login.
   - [views](account/views.py): Views that are related to auth actions like login and logout (We do not enable registration from the WEB UI)

 - __api:__ Application Programming Interface in order to automate resource locking releasing via endpoints.
   - [__ init __](api/__init__.py): Packaging this account directory (Django App) 
   - [apps](api/apps.py): Application configurations 
   - [serializers](api/serializers.py): Serializers Object for the api, to prepare JSON responses.
   - [urls](api/__urls__.py): Endpoints that are enabled after the api prefix
   - [views](api/views.py): Views where we will take actions in each endpoint, depending on the request method.

 - __lockable_resource:__ Application Programming Interface in order to automate resource locking releasing via endpoints.
   - [__ init __](lockable_resource/__init__.py): Packaging this account directory (Django App) 
   - [admin](lockable_resource/admin.py): Model Registrations to the admin panel of the Django Application 
   - [apps](lockable_resource/apps.py): Application configurations
   - [constants](lockable_resource/constants.py): Constants of the lockable resource app, we define there rules for available status types that a lockable resource object can have
   - [exceptions](lockable_resource/exceptions.py): hhh
   - [label_manager](lockable_resource/label_manager.py): Takes responsibility to perform smart retrieving of an available resource by only specifying it's label
   - [models](lockable_resource/models.py): Modelize a schema of the table for different Lockable resources we will manage.
   - [signals](lockable_resource/signals.py): Signals to be triggered once a specific field of lockable resource object changes
   - [urls](lockable_resource/urls.py): Available URL's from the Web UI to manage the lockable resources
   - [views](lockable_resource/views.py): Design of the views and actions to take in GET/POST requests.
   
