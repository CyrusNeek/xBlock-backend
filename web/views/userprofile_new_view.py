from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from web.serializers.user_profile_serializer import UserProfileSerializerNew
from rest_framework.permissions import IsAuthenticated

class UserProfileViewNew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializerNew(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        serializer = UserProfileSerializerNew(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, *args, **kwargs):
    #     user = request.user
    #     user.delete()
    #     return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)