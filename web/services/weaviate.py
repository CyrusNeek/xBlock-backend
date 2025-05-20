from django.conf import settings
from django.db.models import fields
from weaviate.classes.config import Property, DataType, Configure
import weaviate
import json

from django.core.serializers.json import DjangoJSONEncoder


from weaviate.util import generate_uuid5  # Generate a deterministic ID

from weaviate.classes.query import MetadataQuery, Filter, HybridFusion, HybridVector
from weaviate.classes.init import Auth
from weaviate.classes.init import AdditionalConfig, Timeout

import logging
import time
import weaviate.exceptions

import os

logger = logging.getLogger(__name__)


fields_to_weaviate_properties = {
    fields.CharField: DataType.TEXT,
    fields.TextField: DataType.TEXT,
    fields.IntegerField: DataType.INT,
    fields.BigAutoField: DataType.NUMBER,
    fields.DateTimeField: DataType.DATE,
}


# client = weaviate.connect_to_custom(
# http_host="weaviate.xblock.ai",
# http_port="80",
# http_secure=False,
# grpc_host="weaviate.xblock.ai",
# grpc_port="443",
# grpc_secure=False,
# skip_init_checks=True,
# auth_credentials=Auth.api_key("adminkey"),
# )


def retry_query_with_backoff(func, retries=3, backoff_in_seconds=1):
    for attempt in range(retries):
        try:
            return func()
        except weaviate.exceptions.WeaviateQueryError as e:
            if attempt < retries - 1:
                logger.warning(
                    f"Retrying query due to error: {e}. Attempt {attempt + 1}/{retries}")
                # Exponential backoff
                time.sleep(backoff_in_seconds * (2 ** attempt))
            else:
                logger.error(f"Query failed after {retries} attempts")
                raise


class WeaviateManager:
    all_collections = [
        "userProfile",
        "tockBookings",
        "resyReservations",
        "orders"
    ]

    def __init__(self) -> None:
        openai_key = os.getenv("OPENAI_API_KEY")

        self.client = weaviate.connect_to_custom(
            headers = {"X-OpenAI-Api-Key": openai_key},
            http_host=settings.WEAVIATE_URL,
            http_port=80,
            http_secure=False,
            grpc_host=settings.WEAVIATE_URL,
            grpc_port=443,
            grpc_secure=False,
            skip_init_checks=True,
            auth_credentials=Auth.api_key(settings.WEAVIATE_API_KEY),
            additional_config=AdditionalConfig(
                timeout=Timeout(init=30, query=60, insert=2000)
            ),
        )

    def __del__(self):
        if self.client:
            self.client.close()

    def get_object(self, collection_name: str, **kwargs):
        collection = self.get_collection(collection_name)

        filters = []
        for key, value in kwargs.items():
            filters.append(Filter.by_property(key).equal(value))

        result = retry_query_with_backoff(
            lambda: collection.query.fetch_objects(
                filters=Filter.all_of(filters))
        )

        if not result.objects:
            return None

        return str(result.objects[0].uuid)

    def update_object(self, collection_name: str, uuid: str, properties: dict):
        """
        Update an object in the Weaviate collection based on its UUID.

        :param collection_name: The name of the collection (class) in Weaviate.
        :param uuid: The UUID of the object to update.
        :param properties: The properties to update.
        :return: The result of the update operation.
        """
        return self.get_collection(collection_name).data.update(uuid, properties)

    def empty_collection(
        self, name: str, fields: list, references=None, vectorizer_config=None
    ):
        self.client.collections.delete(name)
        self.create_collection(name, fields, references, vectorizer_config)

    def create_collection(
        self, name: str, fields: list, references=None, vectorizer_config=None
    ):
        return self.client.collections.create(
            name,
            vectorizer_config=vectorizer_config
            or Configure.Vectorizer.text2vec_openai(),
            generative_config=Configure.Generative.openai(model="gpt-4"),
            properties=fields,
            references=references,
        )

    def get_collection(self, name: str):
        return self.client.collections.get(name)

    def collection_exists(self, name: str) -> bool:
        try:
            self.get_collection(name)
            return True

        except AttributeError:
            return False

    def create_object(self, name: str, properties: dict):
        return self.get_collection(name).data.insert(properties)

    def create_bulk(self, name: str, data: list[dict]):
        collection = self.get_collection(name)

        with collection.batch.fixed_size(batch_size=200) as batch:
            for record in data:
                try:
                    ref = record.pop("user")
                except:
                    ref = None
                obj_uuid = generate_uuid5(record)
                batch.add_object(
                    properties=json.loads(json.dumps(
                        record, cls=DjangoJSONEncoder)),
                    uuid=obj_uuid,
                )

                if ref != None:
                    batch.add_reference(
                        from_property="user",
                        from_uuid=obj_uuid,
                        to=ref,
                    )

        print(
            collection.batch.failed_objects[0]
            if collection.batch.failed_objects
            else "No errors found during the batch insert"
        )
        # return self.get_collection(name).data.insert_many(data)

    def query_collection(self, name: str, query: str):
        self.get_collection(name).query.bm25(query)

    # def similiar_search(self, collection_name: str, query: str, limit=50):
    #     collection = self.get_collection(collection_name)

    #     return collection.query.near_text(
    #         query,
    #         limit=limit,
    #         return_metadata=MetadataQuery(distance=True)
    #     )

    # def global_similiar_search(self, query: str, limit=10):

    #     logger.info("Querying similar objects " + str(query) + "  -  " + str(limit))
    #     results = {}

    #     for collection_name in self.all_collections:
    #         results[collection_name] = self.similiar_search(collection_name, query, limit)

    #     return results

    # def keyword_search(self, collection_name: str, query: str, limit=50):
    #     collection = self.get_collection(collection_name)

    #     return collection.query.bm25(
    #         query,
    #         limit=limit,
    #         return_metadata=MetadataQuery(score=True)
    #     )

    # def global_keyword_search(self, query: str, limit=10):
    #     results = {}
    #     logger.info("Querying keyword objects " + str(query) + "  -  " + str(limit))

    #     for collection_name in self.all_collections:
    #         results[collection_name] = self.keyword_search(collection_name, query, limit)

    #     return results

    def group_search(self, collection_name: str, query: str):
        raise NotImplementedError()

    def global_search(self, query: str):
        results = {}

        for collection_name in self.all_collections:
            results[collection_name] = self.group_search(
                collection_name, query)

    def hybrid_search(self, collection_name: str, query: str, filter=None, unit_filter=None, limit=5):
        collection = self.get_collection(collection_name)

        if not unit_filter:
            return None

        if collection_name == "userProfile":
            return collection.query.hybrid(
                query=query,
                alpha=0.5,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

        filters = Filter.by_property("unit").equal(unit_filter)

        if filter:
            filters = filters & Filter.by_property("tables").equal(filter)

        return collection.query.hybrid(
            query=query,
            target_vector="embed_time",
            filters=filters,
            alpha=0.5,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )

    def global_hybrid_search(self, query: str, filter=None, unit_filter=None, limit=10):

        logger.info("Querying similar objects " +
                    str(query) + "  -  " + str(limit))
        results = {}

        for collection_name in self.all_collections:
            results[collection_name] = self.hybrid_search(
                collection_name, filter=filter, unit_filter=unit_filter, query=query, limit=limit)

        return results

    def get_last_record(self, collection_name: str):
        """
        Retrieves the last recorded object from the specified collection,
        based on the 'created_at' field.
        """
        collection = self.get_collection(collection_name)

        # Fetch all objects in the collection
        result = collection.query.fetch_objects()

        if not result.objects:
            return None  # No objects found in the collection

        # Check the structure of each object and extract the 'created_at' field correctly
        sorted_objects = sorted(
            result.objects,
            key=lambda obj: obj.properties.get(
                "created_at", None),  # Safely access 'created_at'
            reverse=True
        )

        return sorted_objects[0]  # Return the most recent object

    def add_property(self, collection_name: str, property_name: str, property_type):
        try:
            articles = self.client.collections.get(collection_name)
            articles.config.add_property(
                Property(
                    name=property_name,
                    data_type=property_type
                )
            )
        except Exception as e:
            print("An error occured: ", e)
