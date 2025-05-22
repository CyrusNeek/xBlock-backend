from datetime import datetime
from django.utils.timezone import is_aware, make_naive


# function that select fields and convert django objects to plain string
def queryset_values_list_to_string(queryset_values_list, separator=", "):
    result_strings = []

    for record in queryset_values_list:
        record_strings = []
        for value in record:
            if isinstance(value, datetime):
                # Convert aware datetime to naive datetime in local timezone if necessary
                if is_aware(value):
                    value = make_naive(value)
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif value is None:
                value = "None"
            else:
                value = str(value)
            record_strings.append(value)

        result_strings.append(separator.join(record_strings))

    return "\n".join(result_strings)


def queryset_columns_to_string(columns, model):
    columns_name_string = " ".join(columns)
    columns_knowledge_string = (
        f"Query result for {model} table with columns: " + columns_name_string + ".\n"
    )
    return columns_knowledge_string
