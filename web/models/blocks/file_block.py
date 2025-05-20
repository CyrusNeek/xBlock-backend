from django.db import models
from ..unit_file import UnitFile
from .block import BlockBase
from django.utils import timezone


class FileBlock(BlockBase):
    files = models.ManyToManyField(UnitFile, blank=True, related_name="file_blocks")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
