from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import OracleService, OracleServiceProjectLink, Flavor, Deployment


class FlavorAdmin(admin.ModelAdmin):
    list_display = 'name', 'cores', 'ram', 'disk'


admin.site.register(Flavor, FlavorAdmin)
admin.site.register(Deployment, structure_admin.ResourceAdmin)
admin.site.register(OracleService, structure_admin.ServiceAdmin)
admin.site.register(OracleServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
