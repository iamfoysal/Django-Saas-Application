from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)

    auto_create_schema = True


class Domain(DomainMixin):
    pass
