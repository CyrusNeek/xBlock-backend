from report.models import ToastOrder, ReportUser, ToastItemSelectionDetails, ResyReservation, ToastPayment, TockBooking
from web.models import Assistant
from django.db.models import Q
from django.conf import settings

from openai import OpenAI

from web.models.openai_file import OpenAIFile



def main():
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    assistants = Assistant.objects.filter(~Q(vector_store_id=None))

    for assistant in assistants:
        files = client.beta.vector_stores.files.list(vector_store_id=assistant.vector_store_id)

        for file in files.data:
            file_instance = OpenAIFile.objects.filter(file_id=file.id).first()
            if file_instance:
                assistant.files.remove(file_instance)
            
            try:
                client.beta.vector_stores.files.delete(file_id=file.id, vector_store_id=assistant.vector_store_id)

            except Exception as e:
                print(e)

        assistant.save()

    for file in OpenAIFile.objects.all():
        try:
            client.files.delete(file_id=file.file_id)

        except Exception as e:
            print(e)

    ToastOrder.objects.update(uploaded=False)
    ToastItemSelectionDetails.objects.update(uploaded=False)
    ResyReservation.objects.update(uploaded=False)
    ToastPayment.objects.update(uploaded=False)
    TockBooking.objects.update(uploaded=False)
    ReportUser.objects.update(uploaded=False)

    print("All assistants updated successfully")




if __name__ == "django.core.management.commands.shell":
    main()
