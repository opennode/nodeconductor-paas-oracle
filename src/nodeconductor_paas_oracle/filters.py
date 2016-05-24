import django_filters

from nodeconductor.structure.filters import BaseResourceStateFilter
from .models import Deployment


class DeploymentFilter(BaseResourceStateFilter):
    db_name = django_filters.CharFilter()

    class Meta(BaseResourceStateFilter.Meta):
        model = Deployment
        fields = [
            'db_name',
            'state',
        ]
        order_by = [
            'state',
            # desc
            '-state',
        ]
