from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from web.services import initialize_user_account, provide_access_token, validate_account_is_not_susspended
from django.db import IntegrityError, transaction

import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

User = get_user_model()

class GoogleOAuthAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), audience=GOOGLE_CLIENT_ID
            )
            email = idinfo.get("email")
            name = idinfo.get("given_name")
            family_name = idinfo.get("family_name")
            picture = idinfo.get("picture")
            user, created = User.objects.get_or_create(
                                                        username=email,
                                                        defaults={
                                                            "username": email,
                                                            "email": email,
                                                            "first_name": name,
                                                            "last_name": family_name,
                                                            "full_name": name + " " + family_name,
                                                            "display_name": name + " " + family_name,
                                                            "profile_image_url": picture,
                                                        }
                                                    )  

            validate_account_is_not_susspended(user)

            initialize_user_account(user)
            data = provide_access_token(user)
            return Response(data)
        except IntegrityError:
            return Response({"error": "failed to create user"}, status=400)

        except ValueError as e:
            return Response({"error": "Invalid Google token"}, status=400)
        

    def refresh_access_token(refresh_token):
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            return response.json()  # Contains new access_token and optionally a new id_token
        else:
            raise Exception("Error refreshing access token: " + response.text)
        

        
