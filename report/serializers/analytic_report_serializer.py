from rest_framework import serializers
from report.models import AnalyticReport


class AnalyticReportSerializer(serializers.ModelSerializer):

    class Meta:
        fields = [
            "unit",
            "created_at",
            "status",
            "error_detail",
            "entry_count",
            "datetime",
            "model_name",
            "pk",
        ]
        model = AnalyticReport
