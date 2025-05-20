from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from subscription.models import SubscriptionPlan, UserSubscription
from web.models import User


class UserResorceQuotaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:

            user = User.objects.get(username=request.user)
            print(user)
            user_subscription = UserSubscription.objects.filter(brand_owner=user.affiliation, status=UserSubscription.ACTIVE).first()
            subscription_plan = user_subscription.plan

            if not subscription_plan:
                return Response({"error": "Subscription plan not found"}, status=404)

            data = {
                "stk_minutes": user.stk_minutes,
                "upload_size": user.upload_size,
                "xmeeting_minutes": user.xmeeting_minutes,
                "tokens": user.tokens,
                "daily_meeting_limit": subscription_plan.daily_meeting_limit,
                "daily_stk_limit": subscription_plan.daily_stk_limit,
                "daily_token_limit": subscription_plan.daily_token_limit,
                "daily_upload_limit": subscription_plan.daily_upload_limit,
                "meeting_session_length": subscription_plan.meeting_session_length,
                "stk_session_length": subscription_plan.stk_session_length,
            }

            return Response(data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
