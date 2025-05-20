from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from web.models import Unit

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = get_user_model().objects.select_related("team", "manager", "unit", "role", "affiliation")\
            .prefetch_related("units")\
            .get(pk=request.user.pk)

        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        update_unit = request.data.get("unit")
        data = request.data.copy()
        data.pop("unit", None)

        if update_unit:
            try:
                unit = Unit.objects.get(pk=update_unit)
                request.user.unit = unit
                request.user.save(update_fields=["unit"])
            except Unit.DoesNotExist:
                return Response(
                    {"unit": "Invalid unit ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = UserSerializer(request.user, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)