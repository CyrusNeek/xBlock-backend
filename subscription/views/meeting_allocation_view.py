from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class MeetingAllocationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwrgs):
        user = request.user
        minutes = user.minutes
        if minutes > 0:
            return Response({"detail": f"User have {minutes} minutes for meeting."}, status=status.HTTP_200_OK)
        return Response({"detail":"User does not have enough minutes to use the meeting."}, status=status.HTTP_404_NOT_FOUND)