from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from . import models


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

        # storage
        yield DefaultPriceListItem(
            item_type=STORAGE, key=flavor.name,
            resource_content_type=STORAGE_KEY)

    @classmethod
    def get_used_items(cls, resource):
        return [
            (FLAVOR, resource.flavor.name, 1),
            (STORAGE, STORAGE_KEY, resource.db_size),
        ]
