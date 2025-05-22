from django.contrib import admin
from .models import (
    XMeeting,
    ActionItem,
    EmotionalAnalysis,
    Employee,
    KnowledgeBase,
    QuestionAnswer,
    Recording,
    TechnicalMetadata,
    TopicKeyword,
    XMeetingNote,
    XMeetingParticipant,
    XMeetingTranscript
)

# Inline admin for related models
class ActionItemInline(admin.TabularInline):
    model = ActionItem
    extra = 1

class EmotionalAnalysisInline(admin.TabularInline):
    model = EmotionalAnalysis
    extra = 1

class XMeetingParticipantInline(admin.TabularInline):
    model = XMeetingParticipant
    extra = 1

class XMeetingNoteInline(admin.TabularInline):
    model = XMeetingNote
    extra = 1

class XMeetingTranscriptInline(admin.TabularInline):
    model = XMeetingTranscript
    extra = 1

# Admin for XMeeting
@admin.register(XMeeting)
class XMeetingAdmin(admin.ModelAdmin):
    list_display = ("xmeeting_title", "xmeeting_date", "platform", "xmeeting_type", "organizer")
    search_fields = ("xmeeting_title", "organizer__full_name", "platform")
    list_filter = ("platform", "xmeeting_type", "xmeeting_date")
    inlines = [ActionItemInline, EmotionalAnalysisInline, XMeetingParticipantInline, XMeetingNoteInline, XMeetingTranscriptInline]

# Admin for ActionItem
@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = ("description", "xmeeting", "assigned_to", "due_date", "status", "priority")
    list_filter = ("status", "priority", "due_date")
    search_fields = ("description", "assigned_to__full_name", "xmeeting__xmeeting_title")

# Admin for EmotionalAnalysis
@admin.register(EmotionalAnalysis)
class EmotionalAnalysisAdmin(admin.ModelAdmin):
    list_display = ("xmeeting", "participant", "emotion", "emotion_score", "sentiment", "sentiment_score", "created_at")
    list_filter = ("emotion", "sentiment", "created_at")
    search_fields = ("xmeeting__xmeeting_title", "participant__full_name")

# Admin for Employee
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "department", "job_title", "location")
    search_fields = ("full_name", "email", "department")
    list_filter = ("department", "job_title", "location")

# Admin for KnowledgeBase
@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "source_type", "access_level", "created_date")
    search_fields = ("title", "author__full_name", "keywords")
    list_filter = ("source_type", "access_level", "created_date")

# Admin for QuestionAnswer
@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ("xmeeting", "question", "asked_by", "answered_by", "created_at")
    search_fields = ("question", "xmeeting__xmeeting_title", "asked_by__full_name", "answered_by__full_name")
    list_filter = ("created_at",)

# Admin for Recording
@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("xmeeting", "file_format", "file_size_mb", "duration_minutes", "storage_location", "access_level")
    list_filter = ("file_format", "storage_location", "access_level")
    search_fields = ("xmeeting__xmeeting_title", "recording_url")

# Admin for TechnicalMetadata
@admin.register(TechnicalMetadata)
class TechnicalMetadataAdmin(admin.ModelAdmin):
    list_display = ("source_system", "data_sync_status", "data_retrieval_created_at", "api_call_id")
    list_filter = ("data_sync_status", "source_system", "data_retrieval_created_at")
    search_fields = ("source_system", "api_call_id")

# Admin for TopicKeyword
@admin.register(TopicKeyword)
class TopicKeywordAdmin(admin.ModelAdmin):
    list_display = ("topic_name", "xmeeting", "start_time", "end_time", "importance_score")
    search_fields = ("topic_name", "xmeeting__xmeeting_title")
    list_filter = ("start_time", "end_time")

# Admin for XMeetingNote
@admin.register(XMeetingNote)
class XMeetingNoteAdmin(admin.ModelAdmin):
    list_display = ("xmeeting", "employee", "created_at", "visibility")
    search_fields = ("xmeeting__xmeeting_title", "employee__full_name")
    list_filter = ("created_at", "visibility")

# Admin for XMeetingParticipant
@admin.register(XMeetingParticipant)
class XMeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ("xmeeting", "employee", "role", "attendance_status", "join_time", "leave_time")
    search_fields = ("xmeeting__xmeeting_title", "employee__full_name")
    list_filter = ("role", "attendance_status")

# Admin for XMeetingTranscript
@admin.register(XMeetingTranscript)
class XMeetingTranscriptAdmin(admin.ModelAdmin):
    list_display = ("xmeeting", "language", "confidence_score")
    search_fields = ("xmeeting__xmeeting_title",)
    list_filter = ("language",)
