from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers import FirebaseCloudMessagingSerializer
from ..models import FirebaseCloudMessaging

from drf_spectacular.utils import extend_schema

class FirebaseCloudMessagingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FirebaseCloudMessagingSerializer

    def post(self, request, *args, **kwargs):
        serializer = FirebaseCloudMessagingSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            token = serializer.validated_data.get("token")
            user = request.user
            
            try:
                fcm_token = FirebaseCloudMessaging.objects.get(token=token)
                if fcm_token.user != user:
                    fcm_token.user = user
                    fcm_token.save()
                    message = "Token Updated"
                else:
                    message = 'Token already exists'
            except:
                fcm_token = FirebaseCloudMessaging.objects.create(
                    user=request.user,
                    token=token
                )
                message = 'Token saved successfully'
            return Response({'message': message}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=FirebaseCloudMessagingSerializer)
    def delete(self, request, *args, **kwargs):
        serializer = FirebaseCloudMessagingSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            token = serializer.validated_data.get("token")

            FirebaseCloudMessaging.objects.filter(user=request.user, token=token).delete()
            message = 'Token deleted successfully'
            return Response({'message': message}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)