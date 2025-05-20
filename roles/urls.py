from rest_framework.routers import DefaultRouter
from .views import PermissionCategoryViewSet, RoleViewSet

router = DefaultRouter()

router.register(r"manage", RoleViewSet, basename="roles-management")
router.register(r"permissions", PermissionCategoryViewSet, basename="permissions")

urlpatterns = router.urls
