from .update_assistant_time import task_update_assistant_instruction
from report.tasks.periodic.crawl_events import task_crawl_xcelenergy_events
# from .upload_weaviate import upload_data_to_weaviate
from .update_meetings_diarization import task_update_whisper_diarization
from .empty_tock_booking_weaviate_collection import run_all_weaviate_tasks
from .task_email import send_queued_emails