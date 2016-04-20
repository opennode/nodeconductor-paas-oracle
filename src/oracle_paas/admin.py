from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import OracleService, OracleServiceProjectLink, Deployment


admin.site.register(Deployment, structure_admin.ResourceAdmin)
admin.site.register(OracleService, structure_admin.ServiceAdmin)
admin.site.register(OracleServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
