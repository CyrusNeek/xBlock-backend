import requests
import logging


logger = logging.getLogger(__name__)
class ResyCrawlerAPI:
    def __init__(self, email, password, location_code):
        self.email = email
        self.password = password
        self.base_url = "https://auth.resy.com/1"
        self.api_url = "https://api.resy.com/3"
        self.auth_token = None
        self.service_token = None
        self.venue_id = None
        self.location_code = location_code
        self.analytics_token = None

    def login(self):
        """
        Logs into the Resy API and retrieves the auth token.
        """
        login_url = f"{self.base_url}/auth"
        login_payload = {
            "email": self.email,
            "password": self.password,
            "legacy": True
        }
        response = requests.post(login_url, json=login_payload)
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("token")
            print(f"Login successful, Auth Token: {self.auth_token}")
        else:
            raise Exception(f"Failed to login: {response.text}")

    def fetch_venues(self):
        """
        Fetches the list of venues and stores the venue ID if it matches the location code.
        """
        venues_url = f"{self.base_url}/venues"
        headers = {
            "x-resy-universal-auth": self.auth_token
        }
        response = requests.get(venues_url, headers=headers)
        if response.status_code == 200:
            venues = response.json()
            for venue in venues:
                if venue['location']['code'] == self.location_code:
                    self.venue_id = venue['id']
                    print(f"Matched Venue ID: {self.venue_id}")
                    break
            if not self.venue_id:
                raise Exception(
                    f"No venue found for location code {self.location_code}")
        else:
            raise Exception(f"Failed to fetch venues: {response.text}")

    def venue_auth(self):
        """
        Authenticates a specific venue and retrieves the service tokens.
        """
        venue_auth_url = f"{self.base_url}/auth/venue"
        headers = {
            "x-resy-universal-auth": self.auth_token
        }
        venue_auth_payload = {
            "venue_id": self.venue_id
        }
        response = requests.post(
            venue_auth_url, json=venue_auth_payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data['os_tokens']['auth']
            self.analytics_token = data['os_tokens']['analytics']
            print(
                f"Venue Auth Successful, Auth Token: {self.auth_token}, Analytics Token: {self.analytics_token}")
        else:
            raise Exception(f"Failed to authenticate venue: {response.text}")

    def fetch_reservation_report(self, year, dayofyear):
        """
        Fetches the reservation report using the analytics service token.
        """
        logger.info(f"Fetching reservation report for {year}-{dayofyear}")
        report_url = f"{self.api_url}/analytics/report/core/Reservations"
        headers = {
            "x-resy-services-auth": self.analytics_token
        }
        report_payload = {
            "struct_binds": f'{{"year":"{year}","dayofyear":"{dayofyear}"}}'
        }
        response = requests.post(
            report_url, data=report_payload, headers=headers)
        if response.status_code == 200:
            report = response.json()
            res = self.match_reservations(report)
            return res
            # print("Reservation Report:", report)
        else:
            raise Exception(
                f"Failed to fetch reservation report: {response.text}")

    def match_reservations(self, data):
        """
        Matches the reservation data with the location code.
        """
        res = []
        data_object = data[0].get("data", {}).get("rows", [])
        for item in data_object:
            cols = item.get("cols", [])
            row_data = {}
            data_object = data[0].get("data", []).get("rows")
            row_data["time"] = self.get_value_by_header_name(cols, "Time")
            row_data["service"] = self.get_value_by_header_name(
                cols, "service")
            row_data["guest"] = self.get_value_by_header_name(cols, "Guest")
            row_data["phone"] = self.get_value_by_header_name(cols, "phone")
            row_data["email"] = self.get_value_by_header_name(cols, "email")
            row_data["allergy_tags"] = self.get_value_by_header_name(
                cols, "Allergy_Tags")
            row_data["Guest_Tags"] = self.get_value_by_header_name(
                cols, "Guest_Tags")
            row_data["Visit_Tags"] = self.get_value_by_header_name(
                cols, "Visit_Tags")
            row_data["party_size"] = self.get_value_by_header_name(
                cols, "Party_Size")
            row_data["ticket_type"] = self.get_value_by_header_name(
                cols, "ticket_type")
            row_data["table"] = self.get_value_by_header_name(cols, "table")
            row_data["Total_Visits"] = self.get_value_by_header_name(
                cols, "Total_Visits")
            row_data["status"] = self.get_value_by_header_name(
                cols, "status")
            row_data["Last_Visit"] = self.get_value_by_header_name(
                cols, "Last_Visit")
            row_data["visit_note"] = self.get_value_by_header_name(
                cols, "Visit_Note")
            row_data["special_requests"] = self.get_value_by_header_name(
                cols, "Special_Requests")
            row_data["Guest_Notes"] = self.get_value_by_header_name(
                cols, "Guest_Notes")
            row_data["bio"] = self.get_value_by_header_name(cols, "bio")
            row_data["reserve_number"] = self.get_value_by_header_name(
                cols, "Reservation_id")
            res.append(row_data)
        return res

    @staticmethod
    def get_value_by_header_name(cols, header_name):
        for col in cols:
            if col.get("header", {}).get("name").lower() == header_name.lower():
                return col.get("value")
        raise Exception(f"Header {header_name} not found")
