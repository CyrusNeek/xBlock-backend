from web.views.integrations.constants import ONEDRIVE_API_URL
from web.views.integrations.common import IntegrationLogin

class OneDriveLoginView(IntegrationLogin):
    
    LOGIN_URL = f"{ONEDRIVE_API_URL}/login"
   
        