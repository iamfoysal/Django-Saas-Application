### Django Software-as-a-Service `SAAS` Application setup

<small> This application enables Django powered websites to have multiple tenants via PostgreSQL schemas. A vital feature for every Software-as-a-Service website.

Django provides currently no simple way to support multiple tenants using the same project instance, even when only the data is different. Because we don’t want you running many copies of your project, you’ll be able to have:</small>

- Multiple customers running on the same instance

- Shared and Tenant-Specific data

- Tenant View-Routing

[Django Tenant](https://django-tenants.readthedocs.io/en/latest/install.html) commands:

- `clone_tenant`
- `collectstatic_schemas`
- `create_missing_schemas`
- `create_tenant`
- `create_tenant_superuser`
- `delete_tenant`
- `migrate`
- `migrate_schemas`
- `rename_schema`

#### Project setup : ~

1.  Install [django_tenant](https://django-tenants.readthedocs.io/en/latest/install.html) `pip install django-tenants`

You’ll have to make the following modifications to your `settings.py` file.

2.  Database setup
    <small>

            import os

            DATABASES = {
            'default': {
                'ENGINE': 'django_tenants.postgresql_backend',
                'NAME': os.environ.get('DATABASE_DB', '<DB_NAME>'),
                'USER': os.environ.get('DATABASE_USER', '<DB_USER>'),
                'PASSWORD': os.environ.get('DATABASE_PASSWORD', '<DB_PASSWORD>'),
                'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
                'PORT': os.environ.get('DATABASE_PORT', '5432'),
            }
            }

</small>

3.  <small>You also have to set where your tenant & domain models are located.

        TENANT_MODEL = "customers.Client" # app.Model
        TENANT_DOMAIN_MODEL = "customers.Domain"  # app.Model

</small>

4.  <small> Add the middleware `django_tenants middleware.main.TenantMainMiddleware` to the top of MIDDLEWARE, so that each request can be set to use the correct schema.

        MIDDLEWARE = (
            'django_tenants.middleware.main.TenantMainMiddleware',
            #...
        )

</small>

5.  <small> Add `django_tenants.routers.TenantSyncRouter` to your DATABASE_ROUTERS setting, so that the correct apps can be synced, depending on what’s being synced (shared or tenant).

        DATABASE_ROUTERS = (
            'django_tenants.routers.TenantSyncRouter',
        )

6.  Configure Tenant and Shared Applications
    To make use of shared and tenant-specific applications, there are two settings called `SHARED_APPS` and `TENANT_APPS`. `SHARED_APPS` is a tuple of strings just like `INSTALLED_APPS` and should contain all apps that you want to be synced to `public`. If `SHARED_APPS` is set, then these are the only apps that will be synced to your `public` schema! The same applies for `TENANT_APPS`, it expects a tuple of strings where each string is an app. If set, only those applications will be synced to all your tenants. Here’s a sample setting
    <small>

            SHARED_APPS = (
                'django_tenants',  # mandatory
                'customers', # you must list the app where your tenant model resides in

                'django.contrib.contenttypes',

                # everything below here is optional
                'django.contrib.auth',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.admin',
            )

            TENANT_APPS = (
                # your tenant-specific apps
                'myapp.hotels',
                'myapp.houses',
            )

            INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

</small>

7.  Tenant View-Routing `PUBLIC_SCHEMA_URLCONF`

    We have a goodie called `PUBLIC_SCHEMA_URLCONF`. Suppose you have your main website at `example.com` and a customer at `customer.example.com`. You probably want your user to be routed to different views when someone requests http://example.com/ and http://customer.example.com/. Because django only uses the string after the host name, this would be impossible, both would call the view at `/`. This is where `PUBLIC_SCHEMA_URLCONF` comes in handy. If set, when the `public` schema is being requested, the value of this variable will be used instead of `ROOT_URLCONF`. So for example, if you have

        ROOT_URLCONF = 'myproject.urls'
        PUBLIC_SCHEMA_URLCONF = 'myproject.urls_public'

    When requesting the view `/login/ `from the public tenant (your main website), it will search for this path on `PUBLIC_SCHEMA_URLCONF` instead of `ROOT_URLCONF`.

8.  For default router access and `www.localhost:8000`

        SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

9.  Tenant & Domain Model

    Here’s an example, suppose we have an app named customers and we want to create a model called Client.

        from django.db import models
        from django_tenants.models import TenantMixin, DomainMixin

        class Client(TenantMixin):
            name = models.CharField(max_length=100)
            address = models.CharField(max_length=100)
           (auto_now_add=True)

            # default true, schema will be automatically created and synced when it is saved
            auto_create_schema = True

        class Domain(DomainMixin):
            pass

10. Admin Support

        from django.contrib import admin
        from django_tenants.admin import TenantAdminMixin
        from myapp.models import Client

        @admin.register(Client)
        class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
                list_display = ('name', 'address')

    Now, create schema

        python manage.py create_tenant

        schema name : demo

        name : demo

    then auto migrate and expect `domain` name like:

        domain: demo.localhost
        is primary (leave blank to use 'True'): False

    Need create superuser for this `demo.localhost` server

        python manage.py create_tenant_superuser

        Enter Tenant Schema ('?' to list schemas): demo

    then type `username` and `password`

    run project `python manage.py runserver`

    visit `http://demo.localhost:8000/admin/ `

    or public admin `www.localhost:8000/admin/`
