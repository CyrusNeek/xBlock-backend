import logging

logger = logging.getLogger(__name__)

def parse_quickbooks_report_kv_paris(json_obj: {}, result=None) -> {str: str}:
    """
    Recursively find all non-empty key value pair under ColData field in the json dict.
    If one ColData have multiple values, they will be joined by " | ".

    Example:
    ...
        },
        "Rows": {
            "Row": [
            {
                "ColData": [
                {
                    "id": "11",
                    "value": "Pump"
                },
                {
                    "value": "2890"
                },
                {
                    "value": "25.00"
                },
                {
                    "value": "250.00"
                },
                {
                    "value": "10.00"
                }
                ]
            },
    ...

    => {
        ...
        "Pump": "2890 | 25.00 | 250.00 | 10.00"
        ...
    }

    Args:
        json_obj (_type_): balance sheet report json dict
        result (_type_, optional): _description_. Defaults to None.

    Returns:
        A python dictionary with all non-empty key value pairs.
    """
    if result is None:
        result = {}

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == "ColData":
                value_level = len(value)
                key = value[0]["value"]
                values_list = []
                for i in range(1, value_level):
                    values_list.append(value[i]["value"])

                if key and any(values_list):  # Check if both are non-empty
                    result[key] = " | ".join(values_list)
            else:
                parse_quickbooks_report_kv_paris(value, result)
    elif isinstance(json_obj, list):
        for item in json_obj:
            parse_quickbooks_report_kv_paris(item, result)
    return result


def parse_quickbooks_report_header_to_dict(json_data: {}) -> {}:
    """
    column = json_data["Columns"]["Column"] will be: 
    
    [{'ColType': 'ProductsAndService', 'ColTitle': ''},
    {'ColType': 'Money', 'ColTitle': 'SKU'},
    {'ColType': 'Money', 'ColTitle': 'Qty'},
    {'ColType': 'Money', 'ColTitle': 'Asset Value'},
    {'ColType': 'Money', 'ColTitle': 'Avg Cost'}]

    =>

    {'ProductsAndService': 'SKU | Qty | Asset Value | Avg Cost'}

    Args:
    json_data (list): A list of dictionaries with 'ColType' and 'ColTitle' keys.

    Returns:
    dict: A dictionary with parsed data.
    """
    try:
        logger.info(f"Quickbooks function calling header input: {json_data}")
        if not json_data or not json_data.get("Columns"):
            return {}

        column = json_data["Columns"]["Column"]
        # Initialize the result dictionary
        result = {}

        # Iterate through the list of dictionaries
        col_key = column[0]["ColType"]
        col_vals = []
        for item in column[1:]:
            col_title = item.get("ColTitle")
            if col_title:  # Ensure that col_title is not None before appending
                col_vals.append(col_title)
        result[col_key] = " | ".join(col_vals)
        
        logger.info(f"QuickBooks function calling cleaned data: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing QuickBooks report header: {e}")
        return json_data


def dict_to_plain_string(json_dict: {}) -> str:
    """
    Convert a dictionary to a plain string, so chatgpt can understand it better.
    """
    # Create a list of strings, each containing "key: value"
    items = [f"{key}: {value}" for key, value in json_dict.items()]

    # Join all items into a single string separated by a newline
    return "\n".join(items)
