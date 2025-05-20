from django.urls import path, include

from rest_framework.routers import DefaultRouter

from report.views.celery_view import celery_queues
from report.views.resy_auth_view import ResyAuthUpdateView


from .views.toast_auth_view import ToastAuthViewSet
from .views.tock_auth_view import TockAuthViewSet
from .views import (
    ReportGuestView,
    ReportOrdersView,
    TagsView,
    LocationView,
    ReportUserActivityViewSet,
    ReportUserInfoView,
    ReportEventView,
    ResyAuthViewSet,
    AnalyticReportView,
    IntegrationView
)


router = DefaultRouter()


router.register("toast-auth", ToastAuthViewSet, "toast-auth")
router.register("tock-auth", TockAuthViewSet, "tock-auth")
router.register("resy-auth", ResyAuthViewSet, "resy-auth")



router.register("report-guests", ReportGuestView, "report-guests")
router.register(
    "report-guests/activity", ReportUserActivityViewSet, basename="report-user-activity"
)
router.register("report-orders", ReportOrdersView)
router.register("report-events", ReportEventView)


urlpatterns = [
    path("", include(router.urls)),
    path("tags/", TagsView.as_view()),
    path("locations/", LocationView.as_view()),
    path("analytics-report/", AnalyticReportView.as_view()),
    path("report-guests/<int:pk>/info/", ReportUserInfoView.as_view()),
    path('celery/queues/', celery_queues, name='celery_queues'),
    path('resy-auth-update/<int:pk>/', ResyAuthUpdateView.as_view(), name='resy-auth-update'),
    path('integrations/', IntegrationView.as_view(), name='integrations'),

]
