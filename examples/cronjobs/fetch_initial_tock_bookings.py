from report.models import TockAuth

from report.tasks.periodic.tock_crawler import crawl_tock_from_past

import logging


logger = logging.getLogger(__name__)


def main():
    tocks = TockAuth.objects.all()

    for tock in tocks:
        logger.info(crawl_tock_from_past.delay(tock.pk))


if __name__ == "django.core.management.commands.shell":
    main()
