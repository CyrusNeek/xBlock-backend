from web.models.user import User


GLOBAL_SIMILAR_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "global_similar_search",
        "description": "Perform a similarity search across all collections listed in global_search_collections. keywords related to this function are toast, tock, resy, reservations, guests, orders, integrations, restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return per collection. cannot be more than 100",
                    "default": 10
                },
            },
            "required": ["query"],
        },
    },
}


KEYWORD_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "keyword_search",
        "description": "Execute a keyword-based search within a specified collection using the BM25 algorithm.",
        "parameters": {
            "type": "object",
            "properties": {
                "collection_name": {
                    "type": "string",
                    "description": "The name of the collection to search. choices are (userProfile, orders, tockBookings, meetings, tasks)",
                },
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return. cannot be more than 150",
                    "default": 50
                },
            },
            "required": ["collection_name", "query"],
        },
    },
}


GLOBAL_KEYWORD_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "global_keyword_search",
        "description": "Perform a keyword-based search using BM25 across all collections listed in global_search_collections. keywords related to this function are toast, tock, resy, reservations, guests, orders, integrations, restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return per collection.",
                    "default": 10
                },
            },
            "required": ["query"],
        },
    },
}


def global_keyword_search(user: User, query: str, limit=10):

    return str(manager.global_keyword_search(query, limit))


def keyword_search(user: User, collection_name: str, query: str, limit=10):

    return str(manager.keyword_search(collection_name, query, limit))


def global_similar_search(user: User, query: str, limit=10):

    # return manager.global_similiar_search(query, limit)
    return "Not implemented"



HYBRID_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "hybrid_search",
        "description": "Execute a hybrid-based search which combines the results of a vector search and a keyword (BM25F) search by fusing the two result sets.",
        "parameters": {
            "type": "object",
            "properties": {
                "collection_name": {
                    "type": "string",
                    "description": "The name of the collection to search. choices are (userProfile, orders, tockBookings, meetings, tasks)",
                },
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return. cannot be more than 150",
                    "default": 50
                },
            },
            "required": ["collection_name", "query"],
        },
    },
}


GLOBAL_HYBRID_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "global_hybrid_search",
        "description": "Perform a hybrid-based search which combines the results of a vector search and a keyword (BM25F) search by fusing the two result sets.The execution happens across all collections listed in global_search_collections. keywords related to this function are toast, tock, resy, reservations, guests, orders, integrations, restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of results to return per collection.",
                    "default": 10
                },
            },
            "required": ["query"],
        },
    },
}

def global_hybrid_search(user: User, query: str, limit=10):

    return str(manager.global_hybrid_search(query, limit))


def hybrid_search(user: User, collection_name: str, query: str, limit=10):

    return str(manager.hybrid_search(collection_name, query, limit))
