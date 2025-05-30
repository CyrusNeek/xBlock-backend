from urllib.parse import urlencode
from web.models import Unit, User
from django.db import models
from django.utils.functional import cached_property
from django.conf import settings
from web.services.storage_service import StorageService


import os


class UnitFile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="uploaded_files"
    )
    file_url = models.URLField(max_length=1000)
    file_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_name = models.CharField(max_length=256, blank=True, null=True)
    uploaded = models.BooleanField(default=False)
    file_size = models.FloatField(null=True, blank=True)
    file_type = models.CharField(max_length=20, blank=True, null=True)
    openai_file_id = models.CharField(max_length=64, blank=True, null=True)
    category = models.ForeignKey(
        "web.BlockCategory", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Unit File"
        verbose_name_plural = "Unit Files"

    def __str__(self):
        return f"{self.file_name} - {self.user} - File"

    @cached_property
    def unit(self):
        return self.user.unit

    @cached_property
    def units(self):
        return self.fileblocks.all()

    @property
    def presigned_get_url(self):
        """

        ->             {folder} / {company_name}/{file_name}
        -> object_name: unit-file/Code/2. Jester_Handbook_6.28.23.pdf
        """
        if os.getenv("AMAZON_DEPLOYMENT", "false") == "true":
            object_name = "/".join(self.file_url.split("/")[-3:])
            result = StorageService().generate_presigned_download_url(object_name)

        result = StorageService().generate_presigned_download_url(self.file_url)

        if type(result) == str:
            return result

        if not result[1]:
            return result[0]

        url, query = result

        query_string = urlencode(query)

        return url + "?" + query_string
