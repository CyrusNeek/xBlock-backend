from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google_services.serializers import TaskSerializer
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from google_services.views.calendar_view import get_credentials

class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task_details = serializer.validated_data
            creds = get_credentials(request.user)
            service = build('tasks', 'v1', credentials=creds)

            task = {
                'title': task_details.get('title'),
                'notes': task_details.get('summary', ''),
            }

            due_date = task_details.get('due_date')
            due_time = task_details.get('due_time')
            if due_date:
                if due_time:
                    due_datetime = datetime.combine(due_date, due_time)
                    task['due'] = due_datetime.isoformat() + 'Z'
                else:
                    task['due'] = f"{due_date.isoformat()}T00:00:00.000Z"

            try:
                task = service.tasks().insert(tasklist='@default', body=task).execute()

                response_data = {
                    'task_created': True,
                    'task_id': task.get('id'),
                    'task_link': task.get('selfLink')
                }
                return Response(response_data)

            except HttpError as error:
                print(f"An error occurred: {error}")
                return Response({"error": "Failed to create task"}, status=500)
        else:
            return Response(serializer.errors, status=400)

class DeleteTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        creds = get_credentials(request.user)
        service = build('tasks', 'v1', credentials=creds)

        try:
            service.tasks().delete(tasklist='@default', task=pk).execute()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except HttpError as error:
            return Response({"error": "Failed to delete task", "details": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task_details = serializer.validated_data
            creds = get_credentials(request.user)
            service = build('tasks', 'v1', credentials=creds)

            try:
                task = service.tasks().get(tasklist='@default', task=pk).execute()

                task['title'] = task_details.get('title', task['title'])
                task['notes'] = task_details.get('summary', task['notes'])

                due_date = task_details.get('due_date')
                due_time = task_details.get('due_time')

                if due_date:
                    if due_time:
                        due_datetime = datetime.strptime(f"{due_date} {due_time}", '%Y-%m-%d %H:%M')
                        task['due'] = due_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    else:
                        task['due'] = f"{due_date}T00:00:00.000Z"

                updated_task = service.tasks().update(tasklist='@default', task=pk, body=task).execute()

                response_data = {
                    'task_updated': True,
                    'task_link': updated_task.get('webViewLink')
                }
                return Response(response_data, status=status.HTTP_200_OK)
            except HttpError as error:
                return Response({"error": "Failed to update task", "details": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
