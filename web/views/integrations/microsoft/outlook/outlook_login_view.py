from web.views.integrations.constants import OUTLOOK_API_URL
from web.views.integrations.common import IntegrationLogin

class OutlookLoginView(IntegrationLogin):
    
    LOGIN_URL = f"{OUTLOOK_API_URL}/login"
   
        