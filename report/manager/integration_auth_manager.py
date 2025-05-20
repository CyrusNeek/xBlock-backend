from django.db import models

from web.models import  BlockCategory, Unit

class IntegrationAuthManager(models.Manager):
    def accessible_by_user(self, user):
        accessible_units = Unit.objects.accessible_by_user(user)
        accessible_block_categories = BlockCategory.objects.accessible_by_user(user)

        return self.get_queryset().filter(
            unit__in=accessible_units,
            block_category__in=accessible_block_categories
        )