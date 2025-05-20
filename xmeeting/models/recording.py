from django.db import models
from django.core.validators import MinValueValidator
from .xmeeting import XMeeting
import uuid


class Recording(models.Model):
    class Meta:
        db_table = 'meeting"."xmeeting_recording'

    ACCESS_PUBLIC = "public"
    ACCESS_INTERNAL = "internal"
    ACCESS_RESTRICTED = "restricted"

    ACCESS_LEVEL_CHOICES = [
        (ACCESS_PUBLIC, "Public"),
        (ACCESS_INTERNAL, "Internal"),
        (ACCESS_RESTRICTED, "Restricted"),
    ]

    STORAGE_GOOGLE_DRIVE = "google_drive"
    STORAGE_AWS_S3 = "aws_s3"
    STORAGE_DROPBOX = "dropbox"
    STORAGE_ONEDRIVE = "onedrive"
    STORAGE_BOX = "box"
    STORAGE_GOOGLE_BUCKET = "google_bucket"

    STORAGE_LOCATION_CHOICES = [
        (STORAGE_GOOGLE_DRIVE, "Google Drive"),
        (STORAGE_AWS_S3, "AWS S3"),
        (STORAGE_DROPBOX, "Dropbox"),
        (STORAGE_ONEDRIVE, "OneDrive"),
        (STORAGE_BOX, "Box"),
        (STORAGE_GOOGLE_BUCKET, "Google Bucket"),
    ]

    FORMAT_MP3 = "mp3"
    FORMAT_WAV = "wav"
    FORMAT_AAC = "aac"
    FORMAT_FLAC = "flac"
    FORMAT_OGG = "ogg"

    FORMAT_MP4 = "mp4"
    FORMAT_MKV = "mkv"
    FORMAT_AVI = "avi"
    FORMAT_MOV = "mov"
    FORMAT_WEBM = "webm"

    FILE_FORMAT_CHOICES = [
        (FORMAT_MP3, "MP3"),
        (FORMAT_WAV, "WAV"),
        (FORMAT_AAC, "AAC"),
        (FORMAT_FLAC, "FLAC"),
        (FORMAT_OGG, "OGG"),
        (FORMAT_MP4, "MP4"),
        (FORMAT_MKV, "MKV"),
        (FORMAT_AVI, "AVI"),
        (FORMAT_MOV, "MOV"),
        (FORMAT_WEBM, "WEBM"),
    ]

    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="record"
    )
    recording_url = models.TextField()
    file_format = models.CharField(max_length=10, choices=FILE_FORMAT_CHOICES)
    file_size_mb = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    duration_minutes = models.PositiveIntegerField()
    storage_location = models.CharField(max_length=20, choices=STORAGE_LOCATION_CHOICES)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)
    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.xmeeting} - ({self.file_format}) {self.recording_url} "

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
