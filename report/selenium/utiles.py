import base64
from django.conf import settings
from sendgrid.helpers.mail import Mail
from web.models.queue_email import QueueEmail
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid import SendGridAPIClient


def send_error_report(screenshot_path, msg, subject, type="image"):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails='mr@xBlockai.onmicrosoft.com',
        subject=subject,
        html_content=msg
    )
    with open(screenshot_path, 'rb') as f:
        data = f.read()
        encoded_file = base64.b64encode(data).decode()

    if type == "image":
        attachment = Attachment(
            FileContent(encoded_file),
            FileName('error_screenshot.png'),
            FileType('image/png'),
            Disposition('attachment')
        )
    # load csv file
    if type == "csv":
        attachment = Attachment(
            FileContent(encoded_file),
            FileName('error_screenshot.csv'),
            FileType('text/csv'),
            Disposition('attachment')
        )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent with status code {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")
