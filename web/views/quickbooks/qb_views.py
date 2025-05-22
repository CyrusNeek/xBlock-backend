from rest_framework.decorators import api_view
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from rest_framework.response import Response
import requests
from rest_framework import status
from urllib.parse import urlparse, parse_qs
from django.shortcuts import redirect
from web.models.quickbooks import QBReportJson, QuickBooksCredentials
from .utils import parse_quickbooks_report_kv_paris
from django.utils import timezone
from web.models import Unit, User
from subscription.models import UserSubscription
from web.utils.push_notification import PushNotification


@api_view(["GET", "POST"])
def get_quickbooks_auth_url(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    # Extract unit ID from request data
    unit_id = request.data.get("unit_id")
    user = User.objects.get(pk=request.user.pk)
    user_subscription = UserSubscription.objects.get(
        brand_owner=user.affiliation, status=UserSubscription.ACTIVE
    )

    # Retrieve or initialize the unit based on unit_id
    # Ensure proper error handling if the unit does not exist
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return JsonResponse({"error": "Unit not found"}, status=400)

    # Prepare scopes
    scopes = [Scopes.ACCOUNTING]

    # Instantiate client
    auth_client = AuthClient(
        settings.QB_CLIENT_ID,
        settings.QB_CLIENT_SECRET,
        settings.QB_REDIRECT_URL,
        settings.QB_ENVIRONMENT,
    )

    # Get authorization URL
    auth_url = auth_client.get_authorization_url(scopes)

    # Parse the state from auth_url
    parsed_url = urlparse(auth_url)
    state = parse_qs(parsed_url.query)["state"][0]

    try:
        qb_credentials = QuickBooksCredentials.objects.filter(user=request.user, unit=unit)
        if qb_credentials.exists():
            qb_credentials.update(state=state)
            return JsonResponse({"auth_url": auth_url})

        if user_subscription.total_integration > 0:
            QuickBooksCredentials.objects.create(user=request.user, unit=unit, state=state)
            user_subscription.total_integration -= 1
            user_subscription.save()
            return JsonResponse({"auth_url": auth_url})

        notif = PushNotification()
        notif.send_notification(user=request.user)
        return JsonResponse(
            {"error": "The number of integrations you have exceeds the limit allowed by your subscription plan."},
            status=400,
        )

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@api_view(["GET", "POST"])
def handle_quickbooks_callback(request):
    state = request.GET.get("state", None)
    error = request.GET.get("error", None)
    auth_code = request.GET.get("code", None)

    if error == "access_denied":
        return redirect("sampleAppOAuth2:index")
    if state is None:
        return Response({"error": "State not found"}, status=404)
    if not auth_code:
        return Response({"error": "Authorization code not found"}, status=400)

    realm_id = request.GET.get("realmId", None)

    # Instantiate the AuthClient
    auth_client = AuthClient(
        settings.QB_CLIENT_ID,
        settings.QB_CLIENT_SECRET,
        settings.QB_REDIRECT_URL,
        settings.QB_ENVIRONMENT,
    )

    try:
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)

        # Retrieve the user associated with the state
        credentials = QuickBooksCredentials.objects.get(state=state)
        user = credentials.user

        # Update the user's QuickBooks credentials
        defaults = {
            "access_token": auth_client.access_token,
            "refresh_token": auth_client.refresh_token,
            "realm_id": realm_id,
            "last_success_at": timezone.now(),
            "name": "QuickBooks",
        }
        QuickBooksCredentials.objects.update_or_create(state=state, defaults=defaults)

        # Fetch and save the balance sheet report
        # report_params = {"date_macro": "Last Fiscal Year", "minorversion": "70"}
        # get_quickbooks_balance_sheet_report(
        #     user, realm_id, report_params, auth_client.access_token
        # )

        # Redirect to your React page with a success parameter
        success_url = f"{settings.HUB_BASE_URL}/xblock/all-blocks?status=success?integration=quickbooks"
        return redirect(success_url)

    except QuickBooksCredentials.DoesNotExist:
        return Response({"error": "Invalid state or user not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


def get_quickbooks_balance_sheet_report(user, realm_id, params, access_token):
    # Construct the request URL
    url = f"{settings.QB_BASE_URL}/v3/company/{realm_id}/reports/BalanceSheet"

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    # Make the API request
    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    parsed_result = parse_quickbooks_report_kv_paris(response.json())
    print("parsed_result", parsed_result)

    if response.status_code == 200:
        # Assuming QBReportJson has a field named 'report_json' to store the response
        QBReportJson.objects.update_or_create(user=user, balance_sheet=response.json())
        return True
    else:
        # Handle errors or unsuccessful responses
        return False
