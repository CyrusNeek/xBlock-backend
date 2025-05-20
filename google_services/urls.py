from django.urls import path
from google_services.views import (
    GoogleLoginView,
    GoogleOAuth2CallbackView,
    CreateEventView,
    DeleteEventView,
    CreateTaskView,
    UpdateEventView,
    DeleteTaskView,
    UpdateTaskView,
    CalendarView,
)

urlpatterns = [
    path('login/', GoogleLoginView.as_view(), name='google-login'),
    path('oauth2callback/', GoogleOAuth2CallbackView.as_view(), name='google-oauth2callback'),
    path('calendar/', CalendarView.as_view(), name='fetch_calendar'),
    path('calendar/events/', CreateEventView.as_view(), name='create-calendar-event'),
    path('calendar/events/<str:pk>/', UpdateEventView.as_view(), name='update-calendar-event'),
    path('calendar/events/<str:pk>/delete/', DeleteEventView.as_view(), name='delete-calendar-event'),
    # path('tasks/', CreateTaskView.as_view(), name='create-task'),
    path('tasks/<str:pk>/update/', UpdateTaskView.as_view(), name='update-task'),
    path('tasks/<str:pk>/delete/', DeleteTaskView.as_view(), name='delete-task'),
]