from django.db import models
from django.contrib.postgres.fields import ArrayField
from .block import BlockBase


class URLBlock(BlockBase):
    urls = ArrayField(models.URLField(max_length=200), blank=True, default=list)

    def save(self, *args, **kwargs):
        if isinstance(self.urls, str):
            self.urls = [self.urls]
        super(URLBlock, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
