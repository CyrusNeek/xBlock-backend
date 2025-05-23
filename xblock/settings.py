"""
Django settings for xblock project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
import json
from datetime import timedelta
from corsheaders.defaults import default_headers
from celery.schedules import crontab
from celery.schedules import timedelta
from dotenv import load_dotenv, find_dotenv
from datetime import datetime


import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(find_dotenv())


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-d=(vl8ppddk+h95wy-z$3sydg_-h0m*n-h!a+tycod8dr)72gc")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "0.0.0.0",
    "localhost:8000",
    "192.168.70.253",
    "localhost",
    "api",
    "hub.xblock.ai",
    "app.xblock.ai",
    "app2.xblock.ai",
    "beta.xblock.ai",
    "admin.xblock.ai",
    "stage.xblock.ai",
    "stage-front.xblock.ai",
    "studious-cod-jx7jr4jpv493jj7-8000.app.github.dev",
    "console.brain.xblock.ai",
]
# SECRET_KEY = os.environ.get("SECRET_KEY")

# DEBUG = bool(os.environ.get("DEBUG"))
# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
# ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "constance",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
    "rest_framework",
    "django_celery_results",
    "web.apps.WebConfig",
    "report.apps.ReportConfig",
    "roles.apps.RolesConfig",
    "accounting.apps.AccountingConfig",
    "google_services.apps.GoogleServicesConfig",
    "subscription.apps.SubscriptionConfig",
    "vtk.apps.VTKConfig",
    "xmeeting.apps.XmeetingConfig",
    "customer.apps.CustomerConfig",
    "pos.apps.PosConfig",
    "employee.apps.EmployeeConfig",
    "reservation.apps.ReservationConfig",
]

AUTH_USER_MODEL = "web.User"

CORS_ALLOWED_ORIGINS = [
    "https://sub.example.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://hub.xblock.ai",
    "https://app.xblock.ai",
    "https://app2.xblock.ai",
    "https://beta.xblock.ai",
    "https://stage.xblock.ai",
    "https://stage-front.xblock.ai",
    "http://192.168.70.253:3000",
    "https://effective-umbrella-ww5rv9rqwrxcgxxp-3000.app.github.dev",
    "https://console.brain.xblock.ai",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "baggage",
    "sentry-trace",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "xBlock",
    "DESCRIPTION": "xBlock API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
CONSTANCE_REDIS_CONNECTION = os.getenv("REDIS_URL", "redis://redis:6379/0")
CONSTANCE_BACKEND = "constance.backends.redisd.RedisBackend"
CONSTANCE_BACKEND = "constance.backends.redisd.CachingRedisBackend"
CONSTANCE_REDIS_CACHE_TIMEOUT = 120

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redbeat_redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")
BROKER_TRANSPORT = "redis"
CELERY_BROKER_TRANSPORT = "redis"

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:1337",
    "https://hub.xblock.ai",
    "https://app.xblock.ai",
    "https://admin.xblock.ai",
    "https://beta.xblock.ai",
    "https://stage.xblock.ai",
    "https://stage-front.xblock.ai",
]


STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

S3_UNIT_FILE_FOLDER = "unit-file"
S3_MEETING_RECORDING_FOLDER = "meetings"

# Check if we're in console mode (admin-only interface)
CONSOLE_MODE = os.getenv("CONSOLE_MODE", "").lower() == "true"

# Set the URL configuration based on console mode
if CONSOLE_MODE:
    ROOT_URLCONF = "xblock.console_urls"
else:
    ROOT_URLCONF = "xblock.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "xblock.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DATABASE_NAME", "xblock"),
        "USER": os.getenv("DATABASE_USER", "xblock"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "Xblock123456"),
        "HOST": os.getenv("DATABASE_HOST", "db"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
        "OPTIONS": {
            "connect_timeout": 100,
            'options': '-c search_path=meeting,public,speech_to_knowledge,history',  

        },
    },
    "test": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}


HUB_BASE_URL = "http://localhost:3000" if DEBUG else "https://hub.xblock.ai"
SELENIUM_REMOTE_URL = "http://selenium:4444/wd/hub"
SELENIUM_2_REMOTE_URL = "http://selenium_2:4444/wd/hub"
SELENIUM_3_REMOTE_URL = "http://selenium_3:4444/wd/hub"

MS_TEAMS_SELENIUM_CHANNEL_URL = "https://xblockai.webhook.office.com/webhookb2/19415de3-12e5-4910-8459-716acbc0d608@f6749743-df11-4ef2-8188-21b5a38c8983/IncomingWebhook/53f8d844e0a1424c8be2142e16d0dd22/d7c6658e-aa92-47d8-964f-0eeb642beca1"

# AWS Key - Optional, can be provided via INTEGRATIONS_CREDENTIALS
# Load integration credentials if available
INTEGRATIONS_CREDENTIALS = {}
if os.getenv("INTEGRATIONS_CREDENTIALS"):
    try:
        INTEGRATIONS_CREDENTIALS = json.loads(os.getenv("INTEGRATIONS_CREDENTIALS"))
    except json.JSONDecodeError:
        print("Warning: Could not parse INTEGRATIONS_CREDENTIALS as JSON")

# AWS settings from either direct env vars or integrations credentials
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME") or INTEGRATIONS_CREDENTIALS.get("aws", {}).get("bucket_name")
AWS_REGION = os.getenv("AWS_REGION") or INTEGRATIONS_CREDENTIALS.get("aws", {}).get("region")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") or INTEGRATIONS_CREDENTIALS.get("aws", {}).get("access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") or INTEGRATIONS_CREDENTIALS.get("aws", {}).get("secret_access_key")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_GUEST_ASSISTANT_ID = "asst_z8TR5QAWIMJgvGcxt7vG5iVG"

# Azure Speech Services - Optional, can be provided via INTEGRATIONS_CREDENTIALS
AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY") or INTEGRATIONS_CREDENTIALS.get("azure", {}).get("subscription_key")
AZURE_SERVICE_REGION = os.getenv("AZURE_SERVICE_REGION") or INTEGRATIONS_CREDENTIALS.get("azure", {}).get("service_region")

# Quickbooks
QB_CLIENT_ID = (
    os.getenv("QB_CLIENT_ID_DEVELOPMENT")
    if DEBUG
    else os.getenv("QB_CLIENT_ID_PRODUCTION")
)
QB_CLIENT_SECRET = (
    os.getenv("QB_CLIENT_SECRET_DEVELOPMENT")
    if DEBUG
    else os.getenv("QB_CLIENT_SECRET_PRODUCTION")
)
QB_REDIRECT_URL = (
    "http://localhost:8000/api/quickbooks/auth/callback"
    if DEBUG
    else "https://hub.xblock.ai/api/quickbooks/auth/callback"
)
QB_ENVIRONMENT = "sandbox" if DEBUG else "production"
QB_BASE_URL = (
    "https://sandbox-quickbooks.api.intuit.com"
    if DEBUG
    else "https://quickbooks.api.intuit.com"
)

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Chicago"
CELERY_TIMEZONE = "America/Chicago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "..", "www", "static")
STATIC_URL = "/static/"
# set the static files directory for development
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {  # Define root logger here
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {  # You can add specific loggers for Django or your apps if needed
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,  # Set to False to prevent duplicate logs
        },
        # Add other specific loggers here if necessary
    },
}


CONSTANCE_CONFIG = {
    "CORS_ALLOWED_ORIGINS_EXTRA": (
        "http://localhost:3000,https://test.com,https://xbrain-ai-923738140935.us-west1.run.app,https://oauth2.googleapis.com,https://www.googleapis.com",
        "Comma-separated list of extra allowed origins for CORS, for BetterServer chatbot service",
    ),
    # Meeting tool - Function calling
    "MEETING_TOOL_DESC": (
        "Query meeting information in user's unit.",
        "OpenAI meeting tool function description",
    ),
    "MEETING_TOOL_ARG_FIELDS_DESC": (
        "Included fields in query result",
        "OpenAI meeting tool function argument Fields description",
    ),
    "MEETING_TOOL_ARG_PARTICIPANTS_FILTER_DESC": (
        "Array of participants' first name to filter meetings",
        "OpenAI meeting tool function argument participants_filter description",
    ),
    "MEETING_TOOL_ARG_CREATED_BY_DESC": (
        "Name of meeting creator",
        "OpenAI meeting tool function argument created_by description",
    ),
    "MEETING_TOOL_ARG_CREATED_DATE_FROM_DESC": (
        "Return python date string refer to start period from user's query on meeting created_at date",
        "OpenAI meeting tool function argument created_date_from description",
    ),
    "MEETING_TOOL_ARG_CREATED_DATE_TO_DESC": (
        "End period of meeting created date",
        "OpenAI meeting tool function argument created_date_to description",
    ),
    # Meeting tool - Function calling
    "QUICKBOOKS_TOOL_DESC": (
        "Get quickbooks profit and loss or balance sheet report. The report period will be based on either date_macro, or a specified start_date and end_date from user.",
        "OpenAI quickbooks tool function description",
    ),
    "QUICKBOOKS_TOOL_ARG_REPORT_TYPE_DESC": (
        "Type of report to be generated",
        "OpenAI quickbooks tool function argument report_type description",
    ),
    "QUICKBOOKS_TOOL_ARG_DATE_MACRO_DESC": (
        "Predefined date range of the report. Use if you want the report to cover a standard report date range; otherwise, use the start_date and end_date to cover an explicit report date range.",
        "OpenAI quickbooks tool function argument date_macro description",
    ),
    "QUICKBOOKS_TOOL_ARG_START_DATE_DESC": (
        "Start date of the report, in the format YYYY-MM-DD. start_date must be less than end_date. Used when date_macro is not provided.",
        "OpenAI quickbooks tool function argument start_date description",
    ),
    "QUICKBOOKS_TOOL_ARG_END_DATE_DESC": (
        "End date of the report, in the format YYYY-MM-DD. end_date must be greater than start_date. Used when date_macro is not provided.",
        "OpenAI quickbooks tool function argument end_date description",
    ),
    "QUICKBOOKS_TOOL_ARG_ADDRESS_DESC": (
        "Unit/Restaurant name and address pair for the Toast report. Ask for clarification and provide a list of available address pairs if user did not specify one.",
        "OpenAI quickbooks tool function argument location description",
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Extra Cors Allowed For BetterServe Bot": ("CORS_ALLOWED_ORIGINS_EXTRA",),
    "OpenAI Function Calling Meeting Tool": (
        "MEETING_TOOL_DESC",
        "MEETING_TOOL_ARG_FIELDS_DESC",
        "MEETING_TOOL_ARG_PARTICIPANTS_FILTER_DESC",
        "MEETING_TOOL_ARG_CREATED_BY_DESC",
        "MEETING_TOOL_ARG_CREATED_DATE_FROM_DESC",
        "MEETING_TOOL_ARG_CREATED_DATE_TO_DESC",
    ),
    "OpenAI Function Calling Quickbooks Tool": (
        "QUICKBOOKS_TOOL_DESC",
        "QUICKBOOKS_TOOL_ARG_REPORT_TYPE_DESC",
        "QUICKBOOKS_TOOL_ARG_DATE_MACRO_DESC",
        "QUICKBOOKS_TOOL_ARG_END_DATE_DESC",
        "QUICKBOOKS_TOOL_ARG_START_DATE_DESC",
        "QUICKBOOKS_TOOL_ARG_ADDRESS_DESC",
    ),
}


CELERY_BEAT_SCHEDULE = {
    "task_update_assistant_instruction": {
        "task": "web.tasks.periodic_tasks.update_assistant_time.task_update_assistant_instruction",
        "schedule": timedelta(minutes=5),
    },
    # Weaviate task only runs if Weaviate credentials are configured
    "task_upload_data_to_weaviate":{
        "task": "web.tasks.periodic_tasks.upload_weaviate.upload_data_to_weaviate",
        "schedule": crontab(minute=0, hour="*/3") if WEAVIATE_API_KEY and WEAVIATE_URL else crontab(minute=0, hour=0),  # Run at midnight if not configured
    },
    "task_update_toast_report": {
        "task": "report.tasks.periodic.toast.toast_crawler.task_fetch_toasts_data",
        # "schedule": crontab(minute=0, hour="5,17"),  # 5 AM and 5 PM
        "schedule": timedelta(minutes=1),

    },
    "task_update_tock_reservations": {
        "task": "report.tasks.periodic.tock_crawler.crawl_tocks",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "task_combine_resy_tock_reservations": {
        "task": "report.tasks.periodic.guest_task.combine_tock_and_resy",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    "task_lifetime_calculate": {
        "task": "report.tasks.periodic.guest_task.lifetime_calculate",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "task_update_resy_reservations": {
        "task": "report.tasks.periodic.resy_crawler.get_valid_reservations_resies",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    # "task_update_resy_ratings": {
    #     "task": "report.tasks.periodic.resy_crawler.get_valid_rating_resies",
    #     "schedule": crontab(hour=6, minute=0, day_of_month="1"),
    # },
    # "task_update_weaviate_collection_data_tock_bookings": {
    #     "task": "web.tasks.periodic_tasks.empty_tock_booking_weaviate_collection.run_all_weaviate_tasks",
    #     "schedule": crontab(minute=0, hour="*/2"),
    # },
    "task_crawl_xcelenergy_events": {
        "task": "report.tasks.periodic.crawl_events.task_crawl_xcelenergy_events",
        "schedule": timedelta(hours=4),
    },
    "task_update_whisper_diarization": {
        "task": "web.tasks.periodic_tasks.update_meetings_diarization.task_update_whisper_diarization",
        "schedule": crontab(minute="*/1"),
    },
    "task_update_whisper_classmate_diarization": {
        "task": "vtk.tasks.periodic_tasks.update_classmate_diarization.task_update_whisper_classmate_diarization",
        "schedule": crontab(minute="*/1"),
    },
    "send-queued-emails-every-15-second": {
        "task": "web.tasks.periodic_tasks.task_email.send_queued_emails",
        "schedule": timedelta(seconds=15),
    },
    "allocate_brand_users_usages_task": {
        "task": "subscription.tasks.update_user_allocations.allocate_brand_users_usages",
        "schedule": crontab(hour=0, minute=0),
    },
    "create_action_item_xmeeting": {
        "task": "xmeeting.tasks.periodic_tasks.create_action_item_task.create_action_item_xmeeting",
        "schedule": crontab(minute="*/5"),
    },
    # "task_upload_vtk_data_to_bucket": {
    #     "task": "vtk.tasks.periodic_tasks.upload_vtk_to_bucket.upload_vtk_data_to_bucket",
    #     "schedule": crontab(minute="*/5"),
    # },
    "task_upload_xmeeting_data_to_bucket": {
        "task": "xmeeting.tasks.periodic_tasks.upload_xmeeting_to_bucket.upload_xmeeting_data_in_bucket",
        "schedule": crontab(minute="*/5"),
    },
    "task_upload_employee_data_to_bucket": {
        "task": "employee.tasks.periodic_tasks.upload_employee_to_bucket.upload_employee_data_in_bucket",
        "schedule": crontab(minute="*/5"),
    },
    "task_upload_reservation_data_to_bucket":{
        "task": "reservation.tasks.periodic_tasks.upload_reservation_to_bucket.upload_reservation_data_to_bucket",
        "schedule": crontab(minute="*/5"),
    },
    "task_upload_pos_data_to_bucket": {
        "task": "pos.tasks.periodic_tasks.upload_pos_to_bucket.upload_pos_data_to_bucket",
        "schedule": crontab(minute="*/5"),
    },
    "task_upload_customer_data_to_bucket": {
        "task": "customer.tasks.periodic_tasks.upload_customer_to_bucket.upload_customer_data_in_bucket",
        "schedule": crontab(minute="*/5"),
    },
    "task_create_report_app_new_models_data": {
        "task": "report.tasks.periodic.create_new_models_data.create_report_app_new_models_object",
        "schedule": timedelta(hours=6),
    },
    "task_create_employee_app_new_models_data": {
        "task": "employee.tasks.periodic_task.create_employee_objects.create_employee_app_data",
        "schedule": timedelta(hours=6),
    },
    "task_check_users_subscription": {
        "task": "subscription.tasks.check_users_subscription.check_users_subscription",
        "schedule": timedelta(minutes=1),
    },
    "task_send_subscription_email": {
        "task": "subscription.tasks.send_subscription_email.send_subscription_email",
        "schedule": timedelta(minutes=1),
    },
}


CELERY_RESULT_BACKEND = "django-db"

CELERY_RESULT_EXTENDED = True


#    SSH KEYS CONFIG
SSH_BASE_DIR = ".sshkeys/"


# CRAWL SETTINGS
CRAWL_BASE_CRAWL_SLEEP_IDLE_SECONDS = 100


GOOGLE_STORAGE_BUCKET_NAME = os.environ.get(
    "GCP_BUCKET_NAME", "xblock_beta_storage")
GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]
GOOGLE_API_CREDENTIALS = BASE_DIR / "google_credentials.json"

BUCKET_UNIT_FILE_FOLDER = "unit-file"
BUCKET_MEETING_FOLDER = "meetings"
BUCKET_SSH_KEYS_FOLDER = "sshkeys"

TESTING = "test" in sys.argv


if DEBUG:

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        "IS_RUNNING_TESTS": False,
    }

    if not TESTING:
        INSTALLED_APPS = [
            *INSTALLED_APPS,
            "debug_toolbar",
        ]
        MIDDLEWARE = [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
            *MIDDLEWARE,
        ]


# else:
#     MIDDLEWARE = [
#         *MIDDLEWARE,
#         "xblock.telegram_middleware.TelegramBotMiddleware"
#     ]


#  TELEGRAM MANAGEMENT

TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
TELEGRAM_BOT_GROUP_ID = os.getenv("TELEGRAM_BOT_GROUP_ID")


VERBA_API_URL = os.getenv("VERBA_API_URL")
VERBA_USERNAME = os.getenv("VERBA_USERNAME")
VERBA_PASSWORD = os.getenv("VERBA_PASSWORD")
VERBA_API_WEBSOCKET = os.getenv("VERBA_API_WEBSOCKET")


# Weaviate settings - Optional, can be provided via INTEGRATIONS_CREDENTIALS
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY") or INTEGRATIONS_CREDENTIALS.get("weaviate", {}).get("api_key")
WEAVIATE_URL = os.getenv("WEAVIATE_URL") or INTEGRATIONS_CREDENTIALS.get("weaviate", {}).get("url")

GOOGLE_OATH_CALLBACK_URL = os.getenv("GOOGLE_OATH_CALLBACK_URL")

WEBHOOK_API_KEY = os.getenv("STRIPE_WEBHOOK_API_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
USE_PROXY = os.getenv("USE_PROXY", False)
if DEBUG and USE_PROXY:
    os.environ["http_proxy"] = os.getenv(
        "HTTP_PROXY", "http://localhost:12334")
    os.environ["https_proxy"] = os.getenv(
        "HTTPS_PROXY", "http://localhost:12334")

DAY_TOCK = 20

# Configure Sendgrid to send mail

# Using SendGrid Django email backend
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# Store API key securely in environment variable
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "hello@xblock.ai")
# # Set to True to use sandbox mode in debug
# SENDGRID_SANDBOX_MODE_IN_DEBUG = os.getenv(
#     'SENDGRID_SANDBOX_MODE_IN_DEBUG', False)
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'  # This is the SendGrid user, use 'apikey' as the username
# EMAIL_HOST_PASSWORD = SENDGRID_API_KEY  # SendGrid API Key
# DEFAULT_FROM_EMAIL = 'no-replay@xblock.io'  # Sender email

# Maximum upload size in bytes (e.g., 50 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
