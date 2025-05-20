import logging
from django.conf import settings
import json
import requests
from web.models.quickbooks import QuickBooksCredentials
from web.views.quickbooks.utils import (
    parse_quickbooks_report_kv_paris,
    dict_to_plain_string,
    parse_quickbooks_report_header_to_dict,
)
from roles.permissions import UserPermission
from intuitlib.client import AuthClient
from constance import config
from typing import Optional, Any
import copy

logger = logging.getLogger(__name__)

try:
    auth_client = AuthClient(
        settings.QB_CLIENT_ID,
        settings.QB_CLIENT_SECRET,
        settings.QB_REDIRECT_URL,
        settings.QB_ENVIRONMENT,
    )
except Exception as e:
    logger.error(f"Error connecting to Intuit OAuth client: {e}")

ACCOUNTING_REPORT_TYPES = [
    "BalanceSheet",
    "ProfitAndLoss",
]

DATE_MACROS = [
    "Today",
    "This Week-to-date",
    "This Month-to-date",
    "This Fiscal Quarter-to-date",
    "This Fiscal Year-to-date",
    "Last Week",
    "Last Month",
    "Last Fiscal Quarter",
    "Last Fiscal Year",
    "Previous Fiscal Quarter",
    "Previous Fiscal Year",
    "Yesterday",
    "This Fiscal Quarter",
    "This Fiscal Year",
]

QUICKBOOKS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_quickbooks_business_report",
        "description": config.QUICKBOOKS_TOOL_DESC,
        "parameters": {
            "type": "object",
            "properties": {
                "report_type": {
                    "type": "string",
                    "enum": ACCOUNTING_REPORT_TYPES,
                    "description": config.QUICKBOOKS_TOOL_ARG_REPORT_TYPE_DESC,
                },
                "date_macro": {
                    "type": "string",
                    "enum": DATE_MACROS,
                    "description": config.QUICKBOOKS_TOOL_ARG_DATE_MACRO_DESC,
                },
                "start_date": {
                    "type": "string",
                    "description": config.QUICKBOOKS_TOOL_ARG_START_DATE_DESC,
                },
                "end_date": {
                    "type": "string",
                    "description": config.QUICKBOOKS_TOOL_ARG_END_DATE_DESC,
                },
                "address": {
                    "type": "string",
                    "description": config.QUICKBOOKS_TOOL_ARG_ADDRESS_DESC,
                },
            },
            "required": ["report_type", "address"],
        },
    },
}

def get_dynamic_quickbooks_tool(user):
    # Create a deep copy of the original QUICKBOOKS_TOOL
    dynamic_quickbooks_tool = copy.deepcopy(QUICKBOOKS_TOOL)
    
    # Modify the copied dictionary
    unit_address_enum = [unit.name + " -- " + unit.address for unit in user.all_units if unit.address != ""]
    dynamic_quickbooks_tool["function"]["parameters"]["properties"]["address"]["enum"] = unit_address_enum
    
    logger.info(f"Dynamic Update QuickBooks Tool address arg enum list: {unit_address_enum}")
    return dynamic_quickbooks_tool


def get_quickbooks_credentials(address: str) -> (str, str, str):
    credentials = QuickBooksCredentials.objects.filter(unit__address=address).first()
    if not credentials:
        return None, None, None
    return credentials.refresh_token, credentials.realm_id, credentials.access_token

def refresh_and_update_credentials(address: str, refresh_token: str) -> (str, str):
    auth_client.refresh(refresh_token=refresh_token)
    new_access_token = auth_client.access_token
    new_refresh_token = auth_client.refresh_token
    defaults = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }
    QuickBooksCredentials.objects.update_or_create(unit__address=address, defaults=defaults)
    return new_access_token, new_refresh_token

def make_quickbooks_api_call(
    realm_id: str, 
    report_type: str, 
    access_token: str, 
    date_macro: Optional[str] = None, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
    ) -> Any:
    
    params = {}
    if date_macro:
        params["date_macro"] = date_macro
    elif start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date
    else:
        return {"error": "Invalid date parameters provided", "status_code": 400}
    
    url = f"{settings.QB_BASE_URL}/v3/company/{realm_id}/reports/{report_type}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, params=params)
    logger.info(f"QuickBooks API Call Response: {response.status_code} {response.reason}")
    return response

def parse_quickbooks_report(response: Any) -> str:
    if response.status_code != 200:
        return f"Error: {response.status_code} {response.reason}"
    
    parsed_result = parse_quickbooks_report_kv_paris(response.json())
    parsed_column_header = parse_quickbooks_report_header_to_dict(response.json())
    cleaned_data_table = (
        dict_to_plain_string(parsed_column_header)
        + "\n"
        + dict_to_plain_string(parsed_result)
    )
    
    return cleaned_data_table if parsed_result else "No data found for the report."

def get_quickbooks_business_report(
        report_type: str, 
        address: str,
        user,
        date_macro: Optional[str] = None, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
    
    
    # TODO: refactor permissions and 
    #  Quick book models based on the new implementations on reports and roles
    #  module
    
    # required_permission = [
    #     # "quickbooks_admin", "quickbooks_manager"
    # ]
    
    # # Access check
    # if UserPermission.check_user_permission(user, required_permission):
    #     # If the user is neither admin nor manager, deny access
    #     return "User do not have permission to access QuickBooks report."
    
    refresh_token, realm_id, access_token = get_quickbooks_credentials(address.split(" -- ")[-1])
    if not refresh_token:
        return "QuickBooks credentials not found given the address."
    new_access_token, _ = refresh_and_update_credentials(address, refresh_token)
    
    response = make_quickbooks_api_call(realm_id, report_type, new_access_token, date_macro, start_date, end_date)
    
    return parse_quickbooks_report(response)
