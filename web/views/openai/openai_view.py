from openai import OpenAI
import logging
from django.conf import settings
import json
from web.views.openai.tools.meeting_tool import MEETING_TOOL, meeting_assistant_function
from web.views.openai.tools.quickbooks_tool import (
    QUICKBOOKS_TOOL,
    get_quickbooks_business_report,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tools.task_tool import task_assistant_function, TASK_TOOL

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

tools = [
    # QUICKBOOKS_TOOL,
    # TASK_TOOL,
    # MEETING_TOOL,
]

ASSISTANT_FUNCTIONS = {
    # "get_quickbooks_business_report": get_quickbooks_business_report,
    # "task_assistant_function": task_assistant_function,
    # "meeting_assistant_function": meeting_assistant_function,
}


@api_view(["GET", "POST"])
def openai_chat_view(request):
    data = request.data
    messages = data.get("messages")
    print(messages)
    # model = data.get('model')
    response = client.chat.completions.create(
        model="gpt-4o.1",
        messages=messages,
        tools=[{"type": "file_search"}],
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        # Note: the JSON response may not always be valid; be sure to handle errors
        messages.append(response_message)  # extend conversation with assistant's reply

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = ASSISTANT_FUNCTIONS[function_name]
            function_args = json.loads(tool_call.function.arguments)
            logger.info("function_args", function_args)
            function_response = function_to_call(
                user=request.user,
                **function_args,
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )  # get a new response from the model where it can see the function response

        return Response(
            {
                "message": second_response.choices[0].message.content,
            },
            status=200,
        )

    return Response(
        {
            "message": response_message.content,
        },
        status=200,
    )
