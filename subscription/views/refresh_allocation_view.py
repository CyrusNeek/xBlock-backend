from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from subscription.models import UserSubscription


class RefreshAllocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = request.user.id

        try:
            user_subscription = UserSubscription.objects.get(
                brand_owner__users=user_id, status=UserSubscription.ACTIVE
            )
        except UserSubscription.DoesNotExist:
            return Response(
                {"detail": "Subscription does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user_subscription.end_date <= timezone.now():
            user_subscription.status = UserSubscription.EXPIRED
            user_subscription.save()
            return Response(
                {"detail": "Subscription is expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_result = self.allocate_tokens(user_subscription)
        meeting_result = self.allocate_meetings(user_subscription)

        # Update last_allocation if either tokens or meetings have been allocated
        if token_result == "allocated" or meeting_result == "allocated":
            user_subscription.last_allocation = timezone.now()
            user_subscription.save()

        # Check the results of allocations and return appropriate responses
        if token_result == "allocated" and meeting_result == "allocated":
            return Response(
                {"detail": "Tokens and minutes refreshed."}, status=status.HTTP_200_OK
            )
        elif token_result == "allocated":
            return Response({"detail": "Tokens refreshed."}, status=status.HTTP_200_OK)
        elif meeting_result == "allocated":
            return Response({"detail": "Minutes refreshed."}, status=status.HTTP_200_OK)
        elif token_result and meeting_result:
            # Combine error messages if both allocations fail
            return Response(
                {
                    "detail": f"{token_result.data['detail']} {meeting_result.data['detail']}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif token_result:
            return token_result
        elif meeting_result:
            return meeting_result

        return Response(
            {"detail": "Token or meeting usage period not specified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def allocate_tokens(self, user_subscription):
        current_time = timezone.now()
        subscription_plan = user_subscription.plan
        last_allocation = (
            user_subscription.last_allocation or user_subscription.start_date
        )

        if subscription_plan.token_usage_period:
            allocation_period, period_delta = self.get_allocation_period(
                subscription_plan.token_usage_period
            )
            if current_time - last_allocation >= period_delta:
                total_tokens = subscription_plan.total_token_allocation
                tokens_per_user = total_tokens // subscription_plan.token_user_limit

                if tokens_per_user == 0:
                    return Response(
                        {"detail": "Your tokens for using xbrain have run out."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for user in user_subscription.brand_owner.users.all():
                    user.tokens += tokens_per_user
                    user.save()

                user_subscription.tokens_remaining = (
                    user_subscription.tokens_remaining - total_tokens
                )
                return "allocated"
            else:
                return Response(
                    {
                        "detail": "Not enough time has passed since the last token allocation."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return None

    def allocate_meetings(self, user_subscription):
        current_time = timezone.now()
        subscription_plan = user_subscription.plan
        last_allocation = (
            user_subscription.last_allocation or user_subscription.start_date
        )

        if subscription_plan.meeting_usage_period:
            allocation_period, period_delta = self.get_allocation_period(
                subscription_plan.meeting_usage_period
            )
            if current_time - last_allocation >= period_delta:
                total_minutes = subscription_plan.total_meeting_duration
                minutes_per_user = total_minutes // subscription_plan.meeting_user_limit

                if minutes_per_user == 0:
                    return Response(
                        {
                            "detail": "Your minutes for using xclassmate/meetings have run out."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for user in user_subscription.brand_owner.users.all():
                    user.minutes += minutes_per_user
                    user.save()

                user_subscription.minutes_remaining = (
                    user_subscription.minutes_remaining - total_minutes
                )
                return "allocated"
            else:
                return Response(
                    {
                        "detail": "Not enough time has passed since the last meeting allocation."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return None

    def get_allocation_period(self, usage_period):
        if usage_period == "daily":
            return usage_period, timedelta(days=1)
        if usage_period == "monthly":
            return usage_period, timedelta(days=30)
        raise ValueError("Invalid usage period.")
