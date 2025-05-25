from web.models.user import User


DOCUMENT_SEARCHER_FUNCTION = {
    "type": "function",
    "function": {
        "name": "document_searcher",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for.",
                },
                "single_prompt": {
                    "type": "string",
                    "description": "The prompt to use for the search.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return.",
                },
            },
            "required": ["query", "single_prompt", "limit"],
        },
    },
}

DOCUMENT_IMAGE_SEARCHER_FUNCTION = {
    "type": "function",
    "function": {
        "name": "document_image_searcher",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for.",
                },
                "single_prompt": {
                    "type": "string",
                    "description": "The prompt to use for the search.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return.",
                },
            },
            "required": ["query", "single_prompt", "limit"],
        },
    },
}


def document_searcher(user: User, query: str, single_prompt: str, limit: int):

    collection = manager.get_collection(
        "unitFiles"
    )  # TODO: filter the results based on user permissions

    return collection.generate.near_text(
        query=query,
        single_prompt=single_prompt,
        limit=limit,
    )


def document_image_searcher(user: User, query: str, single_prompt: str, limit: int):


    collection = manager.get_collection(
        "unitFileImages"
    )  # TODO: filter the results based on user permissions

    return collection.generate.near_text(
        query=query,
        single_prompt=single_prompt,
        limit=limit,
    )
