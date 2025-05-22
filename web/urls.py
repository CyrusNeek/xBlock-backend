from django.urls import path
from web.views import UserProfileView
from web.views.category_viewset import CategoryViewSet
from web.views.document_viewset import DocumentUpdateView, DocumentViewSet, DocumentTranslate
from web.views.export_model_viewset import ExportModelListView
from web.views.meeting_viewset import MeetingCategoryViewSet
from web.views.openai import LLMChatViewSet
from web.views.openai.openai_assistant_view import openai_assistant_view, assistant_history_view, get_user_access_levels
from web.views.openai.openai_view import openai_chat_view
from web.views.sub_category_viewset import SubCategoryView
from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework.routers import DefaultRouter
from web.views import (
    GroupViewSet,
    TaskViewSet,
    UserViewSet,
    MeetingViewSet,
    UnitViewSet,
    BrandOwnerViewSet,
    BlockView,
    SendEmailVerificationView,
    VerifyEmailView,
    Setup2FAView,
    Verify2FAView,
    UserSubBrandsViewSet,
    UserProfileImageViewSet,
    BrandImageViewSet,
    WhisperDataView,
    FirebaseCloudMessagingView,
    BlockCategoryViewSet, 
    FileBlockViewSet, 
    URLBlockViewSet, 
    UserBrandsViewSet,
    UserProfileViewNew,
    UserBrandsViewSetNew,
    MeetingQuizViewset,
    ExportModelViewSet,
    UserResorceQuotaView,
    DocumentXbrain,
    GoogleOAuthAPIView,
    ThreadChatViewSet,
    SingleThreadChatViewSet,
    AgendaViewSet,
    MeetingParticipantViewSet,
    MeetingFileViewSet,
    MeetingAddressViewSet,
    BrandInitViewset,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from web.views import TaskViewSet, UnitFileViewSet, ChangePasswordView
from web.views.quickbooks import get_quickbooks_auth_url, handle_quickbooks_callback
from web.views import HasUnreadNotificationsView, NotificationsView, register, resend_otp, update_user, update_wizard_status, send_welcome_email

router = DefaultRouter()
router.register(r"groups", GroupViewSet)
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"users", UserViewSet)
router.register(r"unitfiles", UnitFileViewSet)
router.register(r"brands", UserBrandsViewSet, basename="primary-brand")
router.register(r"sub-brands", UserSubBrandsViewSet, basename="sub-brands")
router.register(r"meetings", MeetingViewSet, basename="meetings")
router.register(r"brandsowner", BrandOwnerViewSet)
router.register(r"units", UnitViewSet, "units")
router.register(r"block-categories", BlockCategoryViewSet)
router.register(r"fileblocks", FileBlockViewSet)
router.register(r"urlblocks", URLBlockViewSet)
router.register(r"threads", ThreadChatViewSet, "threads")
router.register(r"agendas", AgendaViewSet, "agendas")

router.register(r'meeting-participants', MeetingParticipantViewSet)
router.register(r'meeting-files', MeetingFileViewSet)
router.register(r'meeting-files', MeetingFileViewSet)
router.register(r'meeting-address', MeetingAddressViewSet)


single_chat_viewset = SingleThreadChatViewSet.as_view({
    'get': 'list',       
    'post': 'create',    
})


urlpatterns = [
    path("", include(router.urls)),
    # path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"), # for password authentication
    path("token/", views.OtpTokenObtainPairView.as_view(), name="token_otp_obtain_pair"), # for otp authentication
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/firebase/", FirebaseCloudMessagingView.as_view(), name="firebase"),
    path("register/", views.RegisterView.as_view(), name="auth_register"),
    path("quickbooks/auth/", get_quickbooks_auth_url, name="quickbooks_auth"),
    path(
        "quickbooks/auth/callback",
        handle_quickbooks_callback,
        name="quickbooks_auth_callback",
    ),
    path("chat/", openai_chat_view, name="openai_chat"),
    path("assistant/", openai_assistant_view, name="openai_assistant_chat"),
    path("assistant-history/", assistant_history_view, name="assistant_history_view"),
    path("assistant-access-levels/", get_user_access_levels, name="get-user-access-levels"),
    path("user/profile/", UserProfileView.as_view(), name="user-profile"),
    path("user/profile-new/", UserProfileViewNew.as_view(), name="user-profile-new"),
    path("user/profile/image/", UserProfileImageViewSet.as_view(), name="user-profile-image"),
    path("user/resource/", UserResorceQuotaView.as_view(), name="user-resource"),
    path("blocks/", BlockView.as_view(), name="blocks"),
    path("brands-new/", UserBrandsViewSetNew.as_view(), name="primary-brand-new"),
    path("chat-interface-js", views.serve_chat_interface_js, name="chat-interface"),
    path("user/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path('notifications/has-unread/', HasUnreadNotificationsView.as_view(), name='has-unread-notifications'),
    path('notifications/', NotificationsView.as_view(), name='unread-notifications'),
    path('send-verification-email/', SendEmailVerificationView.as_view(), name='send_verification_email'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('setup-2fa/', Setup2FAView.as_view(), name='setup-2fa'),
    path('verify-2fa/', Verify2FAView.as_view(), name='verify-2fa'),
    path('brands/image/<int:brand_id>/', BrandImageViewSet.as_view(), name='brand-image'),
    path('meetings/<int:meeting_id>/diarization/', WhisperDataView.as_view(), name='update_diarization'),
    path('meetings/<int:meeting_id>/quizzes/', MeetingQuizViewset.as_view(), name='meeting_quizzes'),
    

    path('categories/', CategoryViewSet.as_view(), name='category'), 
    path('categories/<int:category_id>/', CategoryViewSet.as_view(), name='category'), 
    path('categories/<int:parent_id>/subcategories/', SubCategoryView.as_view(), name='subcategories-by-parent'),
    path('meetings/category/<int:category_id>/', MeetingCategoryViewSet.as_view(), name='meeting-category'),
    path('export-models/', ExportModelViewSet.as_view(), name='export-model'),
    path('documents/', DocumentViewSet.as_view(), name='documents'),
    path('document/<int:document_id>/', DocumentUpdateView.as_view(), name='update-document'),
    path('document/<int:document_id>/add-to-xbrain/', DocumentXbrain.as_view(), name='add-document-xbrain'),
    path('documents/<int:recording_id>/', DocumentViewSet.as_view(), name='document'), 
    path('documents/<int:recording_id>/<int:export_model_id>/<str:recording_type>/', DocumentViewSet.as_view(), name='document'), 
    path('documents/<int:doc_id>/translate/', DocumentTranslate.as_view(), name='document'), 

    path('export-models/documents/', ExportModelListView.as_view(), name='export-model-list'),
    path('user/register/', register, name='register-user'),
    path('user/user-profile/', update_user, name='update-user'),
    path('user/resend-otp/', resend_otp, name='resend-otp'),

    path('oauth/google/', GoogleOAuthAPIView.as_view(), name='google_oauth'),
    path('user/wizard/status/', update_wizard_status, name='update_wizard_status'),
    path('user/email/send-welcome-email/', send_welcome_email, name='send-welcome-email'),

    path('threads/<uuid:thread_id>/chats/', single_chat_viewset, name='thread-chats'),
    path('brand/init/', BrandInitViewset.as_view(), name='brand-init'),
]