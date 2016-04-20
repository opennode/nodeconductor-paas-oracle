from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import OracleService, OracleServiceProjectLink, Deploy


admin.site.register(Deploy, structure_admin.ResourceAdmin)
admin.site.register(OracleService, structure_admin.ServiceAdmin)
admin.site.register(OracleServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
