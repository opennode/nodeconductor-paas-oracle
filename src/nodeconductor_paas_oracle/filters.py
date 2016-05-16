import django_filters

from .models import Deployment


class DeploymentFilter(django_filters.FilterSet):
    db_name = django_filters.CharFilter()
    state = django_filters.CharFilter()

    class Meta(object):
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
