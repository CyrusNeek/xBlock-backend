from datetime import datetime
from .models import AnalyticReport
import logging


logger = logging.getLogger(__name__)


def log_to_analytic_report(**kwargs):
    """
    Logs a message to the AnalyticReport model.

    Args:
        task_name (str): The name of the task where the error occurred.
        error_message (str): The error message to log.
    """
    kwargs['datetime'] = datetime.now()
    try:
        model_object = AnalyticReport.objects.create(**kwargs)
    except Exception as e:
        logger.error(f"Error when create AnalyticReport: {str(e)}")
