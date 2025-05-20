from web.views.integrations.constants import SLACK_API_URL
from web.views.integrations.common import IntegrationLogin

class SlackLoginView(IntegrationLogin):
    
    LOGIN_URL = f"{SLACK_API_URL}/login"
   
        