from rest_framework import serializers
from vtk.models import XClassmateQuiz


class XClassmateQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = XClassmateQuiz
        fields = "__all__"
