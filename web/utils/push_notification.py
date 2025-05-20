import firebase_admin
from firebase_admin import credentials, messaging
from web.models import FirebaseCloudMessaging, User, Notification


class PushNotification:
    _initialized_app = None

    def __init__(self):
        """
        Initialize the Firebase app with the service account key,
        ensuring it is only initialized once.
        """
        if not PushNotification._initialized_app:
            self.cred = credentials.Certificate("./firebase_credentials.json")
            PushNotification._initialized_app = firebase_admin.initialize_app(self.cred)
        self.app = PushNotification._initialized_app

    def send_notification(self, user, title, body, data=None):
        tokens = (
            FirebaseCloudMessaging.objects.filter(user=user)
            .values_list("token", flat=True)
            .distinct()
        )
        tokens = [token for token in tokens if isinstance(token, str) and token.strip()]

        Notification.objects.create(user=user, title=title, message=body)

        if not tokens:
            return [
                f"No Firebase Cloud Messaging tokens found for user {user.username}"
            ]

        data_payload = {key: str(value) for key, value in (data or {}).items()}

        # Webpush-specific configuration
        webpush_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                icon="https://xblock.ai/wp-content/uploads/2024/01/cropped-xblock-logo-png.png",
                title=title,
                body=body,
            ),
            data=data_payload,
        )

        # Create a multicast message
        message = messaging.MulticastMessage(
            tokens=tokens,
            webpush=webpush_config,
        )

        # Send notifications to each token individually to avoid redundancy
        try:
            # Send messages
            response = messaging.send_each_for_multicast(message, app=self.app)
            responses = [
                f"Success: {resp.success_count} messages sent, {resp.failure_count} failures"
                for resp in response
            ]

        except Exception as e:
            responses = [f"Error sending to tokens: {str(e)}"]

        return responses

    def send_notification_to_all_users(self, title, body, data=None):
        """
        Send a push notification to all users.

        :param title: The title of the notification.
        :param body: The body of the notification.
        :param data: Additional data to send with the notification (optional).
        :return: A list of responses from FirebaseCloudMessaging or an error message.
        """
        users = FirebaseCloudMessaging.objects.values_list("user", flat=True).distinct()
        responses = []
        for user in users:
            user_instance = User.objects.get(pk=user)
            responses.extend(self.send_notification(user_instance, title, body, data))
        return responses

    def send_notification_to_specific_users(self, user_ids, title, body, data=None):
        """
        Send a push notification to a list of specific users.

        :param user_ids: A list of user IDs to whom the notifications will be sent.
        :param title: The title of the notification.
        :param body: The body of the notification.
        :param data: Additional data to send with the notification (optional).
        :return: A list of responses from FirebaseCloudMessaging or an error message.
        """
        responses = []
        for user_id in user_ids:
            try:
                user_instance = User.objects.get(pk=user_id)
                responses.extend(
                    self.send_notification(user_instance, title, body, data)
                )
            except User.DoesNotExist:
                responses.append(f"User with ID {user_id} does not exist.")
            except Exception as e:
                responses.append(
                    f"Error sending notification to user ID {user_id}: {str(e)}"
                )

        return responses

    def remove_invalid_tokens(self, response):
        """
        Remove invalid tokens from the database based on the FirebaseCloudMessaging response.

        :param response: The response object from a FirebaseCloudMessaging message send.
        """
        # Implement logic to parse the response and remove invalid tokens.
        pass
