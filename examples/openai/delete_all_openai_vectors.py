from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def main():
    res = client.beta.vector_stores.list()

    for record in res.data:
        vector_id = record.id
        client.beta.vector_stores.delete(vector_id)


if __name__ == "django.core.management.commands.shell":
    main()
