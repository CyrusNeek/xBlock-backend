from django.contrib import admin
from employee.models import (
    Conversation,
    Department,
    EmergencyContact,
    EmotionalAnalysis,
    Employee,
    EmploymentDetail,
    KnowledgeBaseContribution,
    Manager,
    PerformanceRecord,
    PersonalInformation,
    TechnicalMetaData,
    TrainingAndDevelopment,
    VoiceInteraction,
)

admin.site.register(Conversation)
admin.site.register(Department)
admin.site.register(EmergencyContact)
admin.site.register(EmotionalAnalysis)
admin.site.register(Employee)
admin.site.register(EmploymentDetail)
admin.site.register(KnowledgeBaseContribution)
admin.site.register(Manager)
admin.site.register(PerformanceRecord)
admin.site.register(PersonalInformation)
admin.site.register(TechnicalMetaData)
admin.site.register(TrainingAndDevelopment)
admin.site.register(VoiceInteraction)
