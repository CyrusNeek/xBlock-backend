from django.contrib import admin
from reservation.models import (
    CommunicationLog,
    PreferenceAndRestriction,
    Guest,
    VisitHistory,
    MarketingData,
    Payment,
    Reservation,
    ModificationHistory,
    Restaurant,
    StaffAssignment,
    TechnicalMetadata,
    Waitlist,
)

admin.site.register(CommunicationLog)
admin.site.register(PreferenceAndRestriction)
admin.site.register(Guest)
admin.site.register(VisitHistory)
admin.site.register(MarketingData)
admin.site.register(Payment)
admin.site.register(Reservation)
admin.site.register(ModificationHistory)
admin.site.register(Restaurant)
admin.site.register(StaffAssignment)
admin.site.register(TechnicalMetadata)
admin.site.register(Waitlist)
