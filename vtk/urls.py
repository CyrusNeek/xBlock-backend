from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vtk.views import (
    XClassmateViewSet,
    WhisperDataView,
    XClassmateQuizViewset,
    XClassmateToggleIsAddedXBrainView,
    XClassmateCategoryViewSet,
    ParticipantViewSet
)

router = DefaultRouter()
router.register(r'participants', ParticipantViewSet, basename="participants")
router.register(r"", XClassmateViewSet, basename="xclassmate")

urlpatterns = [
    path(
        "<int:xclassmate_id>/diarization/",
        WhisperDataView.as_view(),
        name="xclassmate_diarization",
    ),
    path(
        "<int:xclassmate_id>/quizzes/",
        XClassmateQuizViewset.as_view(),
        name="xclassmate_quizzes",
    ),
    path(
        "<int:xclassmate_id>/xbrain-report/manage",
        XClassmateToggleIsAddedXBrainView.as_view(),
        name="xclassmate_xbrain",
    ),
        path('category/<int:category_id>/', XClassmateCategoryViewSet.as_view(), name='xclassmate-category'),

    
] + router.urls
