from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from web.serializers import UserProfileImageSerializer
from web.services import GoogleBucket

class UserProfileImageViewSet(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileImageSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        serializer = UserProfileImageSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.profile_image_url:
            GoogleBucket.delete_file(user.profile_image_url)
            user.profile_image_url.delete(save=True)
            return Response({"detail": "Profile image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "User dont have any profile"}, status=status.HTTP_400_BAD_REQUEST)
