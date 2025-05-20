from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import pyotp

class Setup2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        if not user.otp_secret:
            user.generate_otp_secret()
        
        qr_code_url = user.get_qr_code_url()
        if qr_code_url:
            user.multi_factor_auth = True
            return Response({'qr_code_url': qr_code_url}, status=status.HTTP_200_OK)
        return Response({'error': 'Failed to generate QR code URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Verify2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp_code = request.data.get('otp_code') 
        user = request.user

        if user.otp_secret:
            totp = pyotp.TOTP(user.otp_secret)
            if totp.verify(otp_code):
                return Response({'message': '2FA verified successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid OTP code'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': '2FA not enabled'}, status=status.HTTP_400_BAD_REQUEST)

