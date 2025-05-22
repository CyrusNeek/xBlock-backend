from django.contrib import admin
from vtk.models import (
    ContentFeedback,
    ContentType,
    ExportedFile,
    GeneratedContent,
    KnowledgeBase,
    LanguageSupported,
    Recording,
    TechnicalMetadata,
    Transcription,
    VTKUser,
    XClassmate,
    XClassmateQuiz,
    Participant
)

# Customize how models are displayed in the Django Admin interface

@admin.register(ContentFeedback)
class ContentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'feedback_date', 'rating')
    search_fields = ('content__content_text', 'user__email', 'comments')
    list_filter = ('rating', 'feedback_date')


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'description')
    search_fields = ('content_type', 'description')


@admin.register(ExportedFile)
class ExportedFileAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'export_date', 'file_format')
    search_fields = ('content__content_text', 'user__email')
    list_filter = ('file_format', 'export_date')


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'user', 'generation_date', 'status', 'feedback_provided')
    search_fields = ('content_text', 'user__email', 'status')
    list_filter = ('status', 'generation_date')
    date_hierarchy = 'generation_date'


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'language', 'approval_status', 'creation_date')
    search_fields = ('title', 'content', 'user__email')
    list_filter = ('approval_status', 'creation_date', 'language')
    autocomplete_fields = ('user', 'language', 'source_content', 'approver')


@admin.register(LanguageSupported)
class LanguageSupportedAdmin(admin.ModelAdmin):
    list_display = ('language_code', 'language_name', 'is_supported')
    search_fields = ('language_code', 'language_name')
    list_filter = ('is_supported',)


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ('recording_title', 'stk_user', 'recording_date', 'language', 'transcription_status', 'is_uploaded')
    search_fields = ('recording_title', 'user__email')
    list_filter = ('transcription_status', 'recording_date', 'language')
    date_hierarchy = 'recording_date'


@admin.register(TechnicalMetadata)
class TechnicalMetadataAdmin(admin.ModelAdmin):
    list_display = ('process_name', 'source_id', 'status', 'created_at')
    search_fields = ('process_name', 'source_id', 'error_message')
    list_filter = ('status', 'process_name')
    date_hierarchy = 'created_at'


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('recording', 'transcription_service', 'confidence_score', 'transcription_date')
    search_fields = ('recording__recording_title', 'transcription_service')
    list_filter = ('transcription_service', 'transcription_date')
    date_hierarchy = 'transcription_date'


@admin.register(VTKUser)
class VTKUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'date_joined', 'language_preference')
    search_fields = ('email', 'full_name')
    list_filter = ('date_joined', 'language_preference')
    autocomplete_fields = ('language_preference',)


@admin.register(XClassmate)
class XClassmateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'length', 'source_language', 'created_by','file_id')
    search_fields = ('name', 'key_points')
    list_filter = ('created_at',"created_by")
    date_hierarchy = 'created_at'

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name','created_at', 'xclassmate', 'user')
    search_fields = ('full_name', 'created_at')
    list_filter = ('created_at',"user")
    date_hierarchy = 'created_at'


@admin.register(XClassmateQuiz)
class XClassmateQuizAdmin(admin.ModelAdmin):
    list_display = ('x_classmate', 'text', 'created_at')
    search_fields = ('x_classmate__name', 'text')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

