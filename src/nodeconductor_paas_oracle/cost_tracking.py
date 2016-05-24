from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from . import models


TYPE = 'type'
FLAVOR = CostTrackingBackend.VM_SIZE_ITEM_TYPE
STORAGE = 'storage'
STORAGE_KEY = '1 GB'


class OracleCostTrackingBackend(CostTrackingBackend):
    NUMERICAL = [STORAGE]

    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(models.Deployment)

        # flavors
        for flavor in models.Flavor.objects.all():
            yield DefaultPriceListItem(
                item_type=FLAVOR, key=flavor.name,
                resource_content_type=content_type)

        # types
        for v, _ in models.Deployment.Version.CHOICES:
            for t, _ in models.Deployment.Type.CHOICES:
                d = models.Deployment(db_type=t, db_version=v)
                yield DefaultPriceListItem(
                    item_type=TYPE, key=slugify(d.db_version_type),
                    resource_content_type=content_type)

        # storage
        yield DefaultPriceListItem(
            item_type=STORAGE, key=STORAGE_KEY,
            resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, resource):
        return [
            (TYPE, slugify(resource.db_version_type), 1),
            (FLAVOR, resource.flavor.name, 1),
            (STORAGE, STORAGE_KEY, resource.db_size),
        ]
