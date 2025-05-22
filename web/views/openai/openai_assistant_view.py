from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime, timezone
from openai import OpenAI
import logging
import json
import time
import re
import pytz
import base64
from accounting.models.team import Team
from roles.models import Permission
from web.models.block_category import BlockCategory
from web.models.blocks.file_block import FileBlock
from web.views.openai.cors_util import cors_whitelist_extra_from_constance
from web.views.openai.openai_agent import filter_openai_response_objects
from web.models.assistant import Assistant
from web.tasks import task_update_llmchat
from web.models import User, Unit, Notification, Thread, Chat, Meeting, Brand, UserBrand, UnitFile, OpenAIFile, Document
from vtk.models import XClassmate

from subscription.models import UserDailyUsage, UserSubscription
from subscription.tools.decrement_user_tokens import decrement_user_tokens
from fpdf import FPDF
from io import BytesIO
from web.serializers import ThreadChatSerializer
from rest_framework import status
import os
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.auth
from google.oauth2.service_account import Credentials
from web.views import detect_image_text, detect_image_content
from web.services import generate_short_id, calculate_openai_tokens
from web.services.openai_service import OpenAIService
from vtk.services import upload_file_to_gcs, get_presigned_post_url, base64_to_file
from roles.permissions import UserPermission
from roles.constants import UNLIMITED_ANSWER_ACCESS
import openai
from rest_framework.permissions import IsAuthenticated

from web.services.file_service import FileService

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

tools = []

ASSISTANT_FUNCTIONS = {}

RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 40

# ============ consider to remove safely ===============
def before_retry(retry_state):
    if retry_state.attempt_number == 1:
        logger.info(f"Assistant View First Attempt")

    if retry_state.attempt_number > 1:
        logger.info(f"Retry after 1 second... Attempt {retry_state.attempt_number}")


def create_thread_message(thread_id, message, context, file_ids=[]):
    try:

        now = datetime.now(timezone.utc)
                
        content = f"""
                    You are a helpful and informative restaurant reservation assistant. You can access reservation details provided as context in JSON format. Your primary goal is to answer user questions accurately and concisely based on the provided context.  If the context lacks the information needed to answer the question, respond explicitly with "Sorry, I can't help with that just yet as I'm still learning how to be more helpful. But hang tight—I'm getting smarter every day and should be able to answer questions like this soon!". Avoid including any irrelevant information in your responses. 

                    

                    System Instructions: 

                    

                    1. Analyze the provided JSON context thoroughly. Extract all relevant information pertaining to the user's question. An empty JSON object `{{}}` signifies that no data match the criteria implied by the user's query and in this case, the answer should inform the user that no records was found. 

                    2. Answer the user's question directly and concisely. Provide only the necessary information. 

                    3. If the JSON context *does not* contain the information needed to answer the question respond with "Sorry, I can't help with that just yet as I'm still learning how to be more helpful. But hang tight—I'm getting smarter every day and should be able to answer questions like this soon!" Do not guess or invent information.  

                    4. If the JSON is empty `{{}}` and the question pertains to availability, interpret this as no records being found for the specified criteria and answer accordingly (e.g., "There are no reservations at that time."). 

                    5. Do not include any extraneous information or commentary.  Focus solely on answering the user's question. 

                    6. Maintain a professional and helpful tone. 

                    7. Carefully review the user's query to identify any specific dates or times mentioned, ensuring the user's time and date are given after the question. Pay close attention to the user's query to identify any specific time mentioned and the user's time when asking the question, and ensure the matching and correctness between the time of the data and the user's time. 

                    8. When the user asks about table status such as who's on a table, if the context shows a reservation and the value of occupied is 'False', it means that the table is currently empty but is reserved at the time mentioned in the context. The variable occupied states the status of the table. 

                    

                    Context Definitions: 
                    
                    The JSON data provided describes restaurant reservations and includes the following fields: 

                    reservation_count: Total number of reservations matching the user's query. (Numerical value)   
                    guests_count: Total number of guests across all matching reservations. (Numerical value)   
                    reserved_tables: List of table numbers reserved for matching reservations. (List of text values)
                    reservation_date: The date and time of the guest's reservation. (Datetime value)
                    phone: The guest's phone number. (Text value)
                    email: The guest's email address. (Text value)
                    first_name: The guest's first name. (Text value)
                    last_name: The guest's last name. (Text value)
                    lifetime_value: A metric representing the total spending or loyalty level of the guest with the restaurant. (Numerical value)
                    total_visits: The total number of times the guest has visited the restaurant. (Numerical value)
                    occupied: Indicates whether tables are currently occupied. (Boolean value: True or False). (Boolean value) 
                    booking_owner: The person or system that created the reservation. Includes contact details if available. (Text value)
                    guest: The guest's full name. (Text value)
                    party_size: The total number of guests included in the reservation. (Numerical value)
                    status: The current status of the reservation (e.g., "Reserved," "Confirmed," "Cancelled"). (Text value)
                    guest_notes: General notes about the guest (e.g., preferences). (Text value)
                    guest_tags: Labels or tags assigned to the guest's profile (e.g., "VIP," "regular"). (Text value)
                    tables: A list of tables assigned to the reservation. (Text value)
                    confirmation: Confirmation details like a code or link. (Text value)
                    brand: Specifies the restaurant brand associated with the reservation. (Text value)
                    servers: Identifies the server(s) assigned to the reservation. (Text value)
                    birthday: A flag indicating whether the reservation is for a birthday celebration. (Datetime value)
                    service: Specifies the type of meal service (e.g., "breakfast," "lunch," "dinner"). (Text value)
                    time: The specific scheduled time for the guest's reservation. (Time value)
                    visit_note: Specific notes or special instructions for this particular reservation (e.g., "Anniversary", "Birthday celebration"). (Text value)
                    allergy_tags: Indicates any allergies the guest has (e.g., "gluten-free," "peanut allergy"). A null value means no allergies specified. (Text value)
                    special_requests: Any special requests for the reservation. (Text value)
                    ticket_type: The type of reservation. (Text value)



                    

                    Input/Output Examples: 

                    " 

                    Example 1
                    Question: How many reservations are there for lunch today?  
                    Context:
                    {{
                        "reservation_count": 2,
                        "guests_count": 10,
                        "reserved_tables": ["13B", "4"],
                        "reservation_detail": [
                            {{
                                "reservation_date": "2024, 11, 22, 13, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16512426274",
                                "email": "lori.Johnson@gmail.com",
                                "first_name": "Lori",
                                "last_name": "Johnson",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Lori Johnson",
                                "party_size": 4,
                                "status": "Reserved",
                                "guest_notes": null,
                                "guest_tags": null,
                                "tables": "4",
                                "service": "lunch",
                                "time": "13:00:00",
                                "visit_note": " ",
                                "allergy_tags": null,
                                "special_requests": null,
                                "ticket_type": null
                            }},
                            {{
                                "reservation_date": "2024, 11, 22, 19, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16512426274",
                                "email": "lori.parizek@gmail.com",
                                "first_name": "Lori",
                                "last_name": "Parizek",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Lori Parizek",
                                "party_size": 6,
                                "status": "Reserved",
                                "guest_notes": null,
                                "guest_tags": null,
                                "tables": "13B",
                                "service": "dinner",
                                "time": "19:00:00",
                                "visit_note": " ",
                                "allergy_tags": null,
                                "special_requests": null,
                                "ticket_type": null
                            }}
                        ]
                    }}

                    Answer: We have 2 reservations for lunch for today.
                    
                    Example 2
                    Question: Are there any notes for the guests at Table 8?  
                    Context:
                    {{
                        "reservation_count": 1,
                        "guests_count": 4,
                        "reserved_tables": ["4"],
                        "reservation_detail": [
                            {{
                                "reservation_date": "2024, 11, 22, 13, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16512426274",
                                "email": "Tom.13331@gmail.com",
                                "first_name": "Tom",
                                "last_name": "Parizek",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Tom Parizek",
                                "party_size": 4,
                                "status": "Reserved",
                                "guest_notes": null,
                                "guest_tags": null,
                                "tables": "4",
                                "service": "lunch",
                                "time": "13:00:00",
                                "visit_note": " ",
                                "allergy_tags": {{"peanut allergy"}},
                                "special_requests": null,
                                "ticket_type": null
                            }}
                        ]
                    }}

                    Answer: Yes, Table 8 has a note that one guest has a peanut allergy.

                    Example 3
                    Question: Are any tables reserved for a special event? 
                    Context:
                    {{
                        "reservation_count": 0,
                        "guests_count": 0,
                        "reserved_tables": [],
                        "reservation_detail": {{}}
                    }}

                    Answer:  Currently, no tables are reserved for a special event.

                    Example 4
                    Question: Do any guests have notes about special occasions?
                    Context:
                    {{
                        "reservation_count": 3,
                        "guests_count": 10,
                        "reserved_tables": ["1", "13", "17"],
                        "reservation_detail": [
                            {{
                                "reservation_date": "2024, 11, 22, 12, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16543426274",
                                "email": "lori.parizek@gmail.com",
                                "first_name": "Tom",
                                "last_name": "Hanks",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Tom Hanks",
                                "party_size": 2,
                                "status": "Reserved",
                                "guest_notes": {{"hosting a business dinner}},
                                "guest_tags": null,
                                "tables": "1",
                                "service": "lunch",
                                "time": "12:00:00",
                                "visit_note": " ",
                                "allergy_tags": {{"peanut allergy"}},
                                "special_requests": null,
                                "ticket_type": null
                            }},
                            {{
                                "reservation_date": "2024, 11, 22, 15, 30, tzinfo=datetime.timezone.utc",
                                "phone": "+16512499274",
                                "email": "lorin@gmail.com",
                                "first_name": "Tommy",
                                "last_name": "smith",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Tommy smith",
                                "party_size": 5,
                                "status": "Reserved",
                                "guest_notes": {{"celebrating a promotion"}},
                                "guest_tags": null,
                                "tables": "13",
                                "service": "lunch",
                                "time": "15:30:00",
                                "visit_note": null,
                                "allergy_tags": null,
                                "special_requests": null,
                                "ticket_type": null
                            }},
                            {{
                                "reservation_date": "2024, 11, 22, 13, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16512471274",
                                "email": "parizek@gmail.com",
                                "first_name": "Tom",
                                "last_name": "Parizek",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Lori Parizek",
                                "party_size": 3,
                                "status": "Reserved",
                                "guest_notes": {{"celebrating an anniversary"}},
                                "guest_tags": null,
                                "tables": "17",
                                "service": "lunch",
                                "time": "13:00:00",
                                "visit_note": null,
                                "allergy_tags": null,
                                "special_requests": null,
                                "ticket_type": null
                            }}
                        ]
                    }}
                    Answer:  Yes, there are 3 notes: Table 17 is celebrating an anniversary, Table 13 is celebrating a promotion, and Table 1 is hosting a business dinner.

                    Example 5
                    Question: Who is sitting at Table 7? 
                    Context:
                    {{
                        "reservation_count": 1,
                        "guests_count": 6,
                        "reserved_tables": ["7"],
                        "reservation_detail": [
                            {{
                                "reservation_date": "2024, 11, 22, 19, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16993426274",
                                "email": "Miller.parizek@gmail.com",
                                "first_name": "Miller",
                                "last_name": "party",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": True,
                                "guest": "Miller party",
                                "party_size": 6,
                                "status": "Reserved",
                                "guest_notes": {{"hosting a business dinner}},
                                "guest_tags": null,
                                "tables": "7",
                                "service": "dinner",
                                "time": "19:00:00",
                                "visit_note": " ",
                                "allergy_tags": {{"peanut allergy"}},
                                "special_requests": null,
                                "ticket_type": null
                            }},

                        ]
                    }}

                    Answer:  The Miller party, a group of 6, is booked at Table 7 for 7:00 PM and table is occupied.

                    Example 6
                    Question: Who is on Table 13B? 
                    Context:
                    {{
                        "reservation_count": 1,
                        "guests_count": 3,
                        "reserved_tables": ["13B"],
                        "reservation_detail": [
                            {{
                                "reservation_date": "2024, 11, 22, 19, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16993426274",
                                "email": "Miller.Parker@gmail.com",
                                "first_name": "Miller",
                                "last_name": "Parker",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Miller Parker",
                                "party_size": 3,
                                "status": "Reserved",
                                "guest_notes": {{"hosting a business dinner}},
                                "guest_tags": null,
                                "tables": "13B",
                                "service": "dinner",
                                "time": "19:00:00",
                                "visit_note": " ",
                                "allergy_tags": {{"peanut allergy"}},
                                "special_requests": null,
                                "ticket_type": null
                            }},

                        ]
                    }}

                    Answer:  Table 13B is currently not occupied, but there is a reservation by Miller Parker at 7pm.

                    Example 7
                    Question: which tables are occupied? 
                    Context:
                    {{
                        "reservation_count": 2,
                        "guests_count": 10,
                        "reserved_tables": ["13B", "4"],
                        "reservation_detail": [
                            {{
                                "reservation_date": "2024, 11, 22, 13, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16512426274",
                                "email": "lori.Johnson@gmail.com",
                                "first_name": "Lori",
                                "last_name": "Johnson",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Lori Johnson",
                                "party_size": 4,
                                "status": "Reserved",
                                "guest_notes": null,
                                "guest_tags": null,
                                "tables": "4",
                                "service": "lunch",
                                "time": "13:00:00",
                                "visit_note": " ",
                                "allergy_tags": null,
                                "special_requests": null,
                                "ticket_type": null
                            }},
                            {{
                                "reservation_date": "2024, 11, 22, 19, 00, tzinfo=datetime.timezone.utc",
                                "phone": "+16512426274",
                                "email": "lori.parizek@gmail.com",
                                "first_name": "Lori",
                                "last_name": "Parizek",
                                "lifetime_value": "0.00",
                                "total_visits": 0,
                                "occupied": false,
                                "guest": "Lori Parizek",
                                "party_size": 6,
                                "status": "Reserved",
                                "guest_notes": null,
                                "guest_tags": null,
                                "tables": "13B",
                                "service": "dinner",
                                "time": "19:00:00",
                                "visit_note": " ",
                                "allergy_tags": null,
                                "special_requests": null,
                                "ticket_type": null
                            }}
                        ]
                    }}

                    Answer:  There are currently no tables occupied.
                    " 

                    

                    User Query: {message} 

                    Today's Date and Time: {now} 

                    

                    Context: {context} 
                 """

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message if context == {} else content,
            file_ids=file_ids
        )

    except Exception as e:
        """Fail to create message, cancel the run and re-create the message."""
        # Adjusted regex to capture the full thread_id and run_id including 'thread_' and 'run_'
        match = re.search(r"(thread_\w+).*?(run_\w+)", str(e))
        logger.info(f"Fail to create message: {e}")
        if match:
            retrieved_thread_id = match.group(1)
            retrieved_run_id = match.group(2)

            try:
                logger.info(
                    f"Canceling run {retrieved_run_id} in thread {retrieved_thread_id} and re-creating message..."
                )
                run = client.beta.threads.runs.cancel(
                    thread_id=retrieved_thread_id, run_id=retrieved_run_id
                )

                client.beta.threads.messages.create(
                    thread_id=thread_id, role="user", content=message
                )
            except Exception as retry_error:
                logger.info(
                    f"Failed to re-create the message after cancel run. Error: {retry_error}"
                )
        else:
            # The error does not match the expected pattern or is a different type of BadRequestError
            print(f"Encountered a BadRequestError not related to active runs: {e}")


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), before=before_retry, wait=wait_fixed(1))
def create_and_wait_for_run(thread_id, message, user, context=None, message_type="Knowledge"):

    # Default assistant ID
    assistant_id = settings.OPENAI_GUEST_ASSISTANT_ID

    # Dispatch task to update LLM chat
    task_update_llmchat.delay(
        thread_id=thread_id, user_id=user.id if user.is_authenticated else None
    )

    # If user is authenticated and has units, attempt to assign the user-specific assistant ID
    if user.is_authenticated and user.units.exists():
        user_assistant = Assistant.objects.filter(
            user=user, purpose=Assistant.PURPOSE_DEFAULT
        ).first()
        if user_assistant and user_assistant.assistant_id:
            assistant_id = user_assistant.assistant_id
        else:
            logger.warning(
                f"No assistant found for user {user.name}. Using default assistant ID."
            )

    # Attempt to create a message in the thread
    create_thread_message(thread_id, message, context)

    # Create run with appropriate tools and instructions
    if user.is_authenticated and (user.units.exists() or user.unit.exist()):
        logger.info(f"Dynamically assigning tools for user {user.name}...")

        if message_type == "Knowledge":
            tools = [{"type": "file_search"}]
        else:
            tools = []

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            tools=tools,
            model="gpt-4o.1",
        )
    elif user.is_authenticated:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            additional_instructions="Notifying user that they do not have any units associated with their account, please contact support.",
            model="gpt-4o.1",
        )
    else:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            model="gpt-4o.1",
        )

    return wait_for_run(thread_id, run.id)


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), before=before_retry, wait=wait_fixed(1))
def wait_for_run(thread_id, run_id, timeout=TIMEOUT_SECONDS):
    start_time = time.time()
    while time.time() - start_time < timeout:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        logger.info(f"status: {run.status}")
        if run.status in ["completed", "requires_action"]:
            return run
        time.sleep(2)
    logger.info("timeout")
    raise TimeoutError(
        f"Run did not complete after waiting for {TIMEOUT_SECONDS} seconds."
    )


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), before=before_retry, wait=wait_fixed(1))
def prepare_response(thread_id, run, user=None):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response_message = messages.data[0].content[0].text.value
    task_update_llmchat.delay(
        thread_id=thread_id, user_id=user.id if user.is_authenticated else None
    )
    return Response(
        {
            "threadId": thread_id,
            "run": run.id,
            "message": response_message,
        },
        status=200,
    )


def handle_requires_action(thread_id, result_run, user):
    tool_outputs = process_tool_calls(
        result_run.required_action.submit_tool_outputs.tool_calls, user
    )
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id, run_id=result_run.id, tool_outputs=tool_outputs
    )
    run = wait_for_run(thread_id, run.id)

    if run and run.status == "completed":
        return prepare_response(thread_id, run, user)

    return Response(
        {"message": "Assistant requires action but did not complete after processing."},
        status=400,
    )


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), before=before_retry, wait=wait_fixed(1))
def process_tool_calls(tool_calls, user):
    tool_outputs = []
    for i, tool_call in enumerate(tool_calls):
        function_name = tool_call.function.name
        function_to_call = ASSISTANT_FUNCTIONS[function_name]
        function_args = json.loads(tool_call.function.arguments)
        logger.info(f"Processing {i+1}th tool function_args: {function_args}")
        function_response = function_to_call(user=user, **function_args)
        logger.info(f"function_response: {function_response}")
        tool_outputs.append({"tool_call_id": tool_call.id, "output": function_response})
    return tool_outputs

#===========================

@api_view(["GET", "POST"])
@cors_whitelist_extra_from_constance()
@permission_classes([IsAuthenticated])
def openai_assistant_view(request):
    data = request.data
    message = data.get("message")
    user = request.user
    
    thread_id = data.get("threadId")
    base64_image = data.get("image")
    message_type = data.get("type")

    input_tokens = calculate_openai_tokens(message)
    decrement_user_tokens(user.id, input_tokens)

    
    
    if base64_image:
        save_chat_image(chat, base64_image)

    if thread_id:
        thread = Thread.objects.get(id=thread_id)
        openai_thread_id = thread.openai_threadid

    if not thread_id or not thread:
        openai_thread = OpenAIService.create_thread()
        openai_thread_id = openai_thread.id

    
    
    chat = create_chat(request,message, openai_thread_id, is_assistant_thread=True)
    file_ids = find_all_accessible_files(user)
    assistant = Assistant.objects.filter(user=user).first()
    context = get_context_based_on_type(message, message_type, user)

    
    result = OpenAIService.create_message_in_thread(openai_thread_id, message, context, file_ids )
    run = OpenAIService.create_run(openai_thread_id, assistant.assistant_id)
    response =  provide_assistant_response(openai_thread_id, run.id)
    save_chat_response(chat, response)

    response_tokens = calculate_openai_tokens(response)
    decrement_user_tokens(user.id , 4 * response_tokens) # === output calc 4 times input

    response_voice = None
    if message_type == "voice":
        response_voice , err = text_to_speech(response)
        decrement_user_tokens(user.id, response_tokens * 32 )

    return Response(
        { "message": response ,
         "threadId" : chat.thread.id , 
          "voice" : response_voice },
        status=200,
    )


@api_view(["GET"])
@cors_whitelist_extra_from_constance()
@permission_classes([IsAuthenticated])
def get_user_access_levels(request):
    user = request.user
    accessible_file_ids = find_all_accessible_files(user)
    assistant = Assistant.objects.filter(user=user).first()

    vector_store = OpenAIService.create_vector_store(
        "assistant vectorestore",
    )
    for file_id in accessible_file_ids:
        OpenAIService.attach_file_to_vector_store(vector_store.id, file_id)

    user_info_file_id = create_user_info_file(user)
    OpenAIService.attach_file_to_vector_store(vector_store.id, user_info_file_id)
    if(user.file_id):
        OpenAIService.delete_file(user.file_id)
    user.file_id = user_info_file_id
    user.save()

    OpenAIService.update_assistant_vectore_store(assistant.assistant_id, vector_store.id)

    return Response({
        'accessible_file_ids': accessible_file_ids,
        'assistant_id': assistant.assistant_id if assistant else None,
        'vector_store_id': vector_store.id
    })

    


def create_user_info_file(user: User):
    try:
        # Handle user basic info with null checks
        user_info = (
            f"User info --> "
            f"full name: {user.full_name or 'N/A'} - "
            f"email: {user.email or 'N/A'} - "
            f"phone: {user.phone_number or 'N/A'} - "
            f"current unit: {user.unit.name if user.unit else 'N/A'} - "
            f"role: {user.role.label if user.role else 'N/A'} -"
        )
        
        # Handle brands info with null checks
        bussiness_info = ""
        if user.affiliation:
            brands = Brand.objects.filter(owner__id=user.affiliation.id).prefetch_related("units")
            for brand in brands:
                units_info = [
                    f"name: {unit.name} - "
                    f"address: ({unit.address or 'N/A'}) - "
                    f"website: {unit.website or 'N/A'}"
                    for unit in brand.units.all()
                ]
                brand_type = "sub brand" if brand.affiliation else "primary brand"
                bussiness_info += f"{brand_type}: {brand.name} -\n units: {', '.join(units_info)}\n"
        
        # Handle teams info with null checks
        team_info = ""
        if user.unit:
            teams = Team.objects.filter(units=user.unit)
            for team in teams:
                units_info = [
                    f"name: {unit.name} - "
                    f"address: ({unit.address or 'N/A'}) - "
                    f"website: {unit.website or 'N/A'}"
                    for unit in team.units.all()
                ]
                team_info += f"\n team or department: {team.name} -\n units: {', '.join(units_info)}\n"

        # Handle employees info with null checks
        employee_info = ""
        employees = User.objects.filter(units__in=user.all_units).distinct('id')
        for employee in employees:
            employee_info += (
                f"\n employee: {employee.full_name or 'N/A'} - "
                f"email: {employee.email or 'N/A'} - "
                f"phone: {employee.phone_number or 'N/A'} - "
                f"role: {employee.role.label if employee.role else 'N/A'} - "
                f"manager: {employee.manager.full_name if employee.manager else 'N/A'} -\n"
            )

        # Handle permissions info with null checks
        permissions_info = "Access levels and permissions -->"
        if user.role:
            permissions = user.role.permissions.all()
            for permission in permissions:
                permissions_info += f"\n {permission.label or 'N/A'}  -\n"

        # Handle block categories info with null checks
        block_category_info = "Block categories -->"
        if user.unit:
            block_categories = BlockCategory.objects.filter(units=user.unit)
            for block_category in block_categories:
                block_category_info += f"\n {block_category.name or 'N/A'}  -\n"

            # Handle blocks info with null checks
            block_categories_block_info = "Block categories blocks -->"
            blocks = FileBlock.objects.filter(category__in=block_categories)
            for block in blocks:
                block_categories_block_info += (
                    f"\n {block.name or 'N/A'} - "
                    f"created date: {block.created_at or 'N/A'}  -\n"
                )
        else:
            block_categories_block_info = "Block categories blocks --> No blocks available"

        pdf_text = (
            f"{user_info}\n"
            f"{bussiness_info}\n"
            f"{team_info}\n"
            f"{employee_info}\n"
            f"{permissions_info}\n"
            f"{block_category_info}\n"
            f"{block_categories_block_info}"
        )
        
        pdf = FileService.create_pdf_from_text(pdf_text, "user-business-info")
        file = OpenAIService.upload_file(pdf)
        return file.id

    except Exception as e:
        # Log the error and return a default response or raise the exception
        print(f"Error in create_user_info_file: {str(e)}")
        return None  # Or raise the exception if you want to handle it at a higher level

@api_view(["GET", "POST"])
@cors_whitelist_extra_from_constance()
@permission_classes([IsAuthenticated])
def assistant_history_view(request):
    data = request.data
    message = data.get("message")
    user = request.user
    
    thread_id = data.get("threadId")
    base64_image = data.get("image")
    message_type = data.get("type")

    if not message:
        return Response({ "updated" : False, "threadId" : thread_id })

    if not thread_id:
        openai_thread = OpenAIService.create_thread()
        openai_thread_id = openai_thread.id
    else:
        thread = Thread.objects.filter(pk=thread_id).first()
        openai_thread_id = thread.openai_threadid

    chat = create_chat(request, message, openai_thread_id, is_assistant_thread=False)
    tokens = calculate_openai_tokens(message)
    decrement_user_tokens(user.id , tokens)
    return Response({ "updated" : True, "threadId" : chat.thread.id })

def get_context_based_on_type(message, message_type, user):
    context = {}
    if message_type.lower() == "operation" :
        context = filter_openai_response_objects(message, user.pk)
    return context

def provide_assistant_response(thread_id, run_id):
    retries = 50  
    delay = 1  # Delay between retries in seconds

    run_progress = OpenAIService.retrieve_run(thread_id, run_id)
    
    while retries > 0 and run_progress.status != "completed":
        retries -= 1
        time.sleep(delay)  
        run_progress = OpenAIService.retrieve_run(thread_id, run_id)
        
    if run_progress.status == "completed":
        messages = OpenAIService.get_thread_messages(thread_id)

        assistant_message = None
        for msg in (messages):  
            if msg["role"] == "assistant":
                assistant_message = msg  
                break
        return assistant_message["content"]
        
    
    return "Failed to get a response after multiple retries."
    

def find_all_accessible_files(user):
    files = []
    unit_files = get_unit_files(user) 
    meeting_files = find_classmate_and_meeting_files(user) 
    document_files = get_document_files(user)

    onboarding_file = ["file-HDyo3eNruksWbWxcxqQUpZ"] 

    files = unit_files + meeting_files + document_files + onboarding_file

    return files

    
def find_classmate_and_meeting_files(user):
    users = User.objects.filter(id=user.id)  

    if UserPermission.check_user_permission(user, UNLIMITED_ANSWER_ACCESS):
        user_brands = UserBrand.objects.filter(user=user)
        brand_ids = [user_brand.brand.id for user_brand in user_brands]

        primary_brand = Brand.objects.filter(id__in=brand_ids, affiliation=None).first()
        
        if primary_brand:  
            user_brands = UserBrand.objects.filter(brand_id=primary_brand)
            user_ids = [user_brand.user.id for user_brand in user_brands]  
            
            users = User.objects.filter(id__in=user_ids)

    classmates = XClassmate.objects.filter(is_added_xbrain=True,created_by__in=users)
    meetings = Meeting.objects.filter(is_added_xbrain=True,created_by__in=users)
    files = []
    for classmate in classmates :
        if classmate.file_id:
            files.append(classmate.file_id)
    for meeting in meetings :
        if meeting.file_id:
            files.append(meeting.file_id)
    return files

def create_chat(request,message, openai_thread_id, is_assistant_thread=False):
    data = request.data
    user = request.user 

    thread_id = data.get('threadId')
    prompt = message or "New Thread"
    chat_type = data.get('type')
    role = data.get('role')
    if not thread_id:
        thread = create_thread(prompt, user, openai_thread_id, is_assistant_thread=is_assistant_thread)
    else:
        thread = Thread.objects.filter(id=thread_id).first()

    chat = Chat()
    chat.user = user 
    chat.thread = thread
    chat.prompt = prompt
    chat.chat_type = chat_type
    if role:
        chat.role = role
        if role == "assistant" :
            chat.response = message
            chat.prompt = None
        
    chat.save()
    
    return chat
        

def create_thread(prompt, user, openai_thread_id, is_assistant_thread=False):
    thread_title = prompt[:50]  # Set first 50 character as a thread title
    thread = Thread.objects.create(user=user, title=thread_title, openai_threadid=openai_thread_id, is_assistant_thread=is_assistant_thread)
    return thread
 
def create_chat_response(chat : Chat):
    
    token = get_service_account_token()

    url = "https://xbrain-ai-923738140935.us-west1.run.app/predict"
    
    data = {
        "prompt" : chat.prompt ,
        "user_id": [str(chat.user.id)],
        "unit_id": [chat.user.unit.id],
        "type" : chat.chat_type,
        "thread_id" : [str(chat.thread.id)]
        
    }
    headers = {
        "Authorization" : f"Bearer {token}"
    }
    response = requests.post(url,json=data ,headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None
    
def save_chat_response(chat , response):
    chat.response = response
    chat.save()

def save_chat_image(chat, base64_image):
    recording_file_url = upload_chat_image(base64_image)
    text = detect_image_content(base64_image)
    chat.media_url = recording_file_url
    chat.media_content = text[0]
    chat.media_type = "image"
    chat.save()

def upload_chat_image(base64_image):
    file_id = generate_short_id()
    filename = f"chat/{file_id}.jpg".replace( " ", "_")
    presigned_url, data = get_presigned_post_url(file_name=filename)
    
    recording_file_url = presigned_url
    uploaded_file = base64_to_file(base64_image)
    upload_file_to_gcs(presigned_url,data, uploaded_file)
    return recording_file_url+filename

def get_service_account_token():
    import os
    import json
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

    # Get credentials from environment variable
    gcp_credentials_json = os.getenv('GCP_CREDENTIALS')
    
    if gcp_credentials_json:
        # Use credentials from environment variable
        service_account_info = json.loads(gcp_credentials_json)
        credentials = service_account.IDTokenCredentials.from_service_account_info(
            service_account_info,
            target_audience="https://xbrain-ai-923738140935.us-west1.run.app"
        )
    else:
        # Fallback for local development if needed
        json_file_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'xbrain_credential.json')
        credentials = service_account.IDTokenCredentials.from_service_account_file(
            json_file_path,
            target_audience="https://xbrain-ai-923738140935.us-west1.run.app"
        )

    request = Request()
    credentials.refresh(request)

    token = credentials.token
    return token 

def get_unit_files(user):
    units = user.units.all()
    files = []
    block_categories = user.role.block_category.all()
    unit_files = OpenAIFile.objects.filter(unit__in=units, block_category__in=block_categories)
    for unit_file in unit_files:
        files.append(unit_file.file_id)
    return files

def get_document_files(user):
    units = user.units.all()
    files = []
    block_categories = user.role.block_category.all()
    documents = Document.objects.filter(is_added_xbrain=True, unit__in=units, block_category__in=block_categories)
    for document in documents:
        if document.file_id:
            files.append(document.file_id)
    return files


def transcribe_audio(wav_file):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }
    
    files = {
        "file": (wav_file.name, wav_file, "audio/wav")
    }
    
    data = {
        "model": "whisper-1"
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json().get("text")
    else:
        return f"Error: {response.status_code}, {response.text}"

def text_to_speech(text):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        audio_bytes = response.content
        base64_audio = base64.b64encode(audio_bytes).decode("utf-8")  
        return base64_audio, None  
    else:
        return None, response.text 
    
    


    
