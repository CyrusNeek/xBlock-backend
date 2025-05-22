from .views import TeamView
from rest_framework.routers import DefaultRouter



router = DefaultRouter()


router.register("teams", TeamView)


urlpatterns = [] + router.urls

