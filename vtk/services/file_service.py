import base64
from io import BytesIO

def base64_to_file(base64_string, filename="file"):
    """
    Converts a Base64 string into a file-like binary object.

    :param base64_string: The Base64-encoded string.
    :param filename: The name of the file (default: "file").
    :return: A file-like binary object ready for upload or processing.
    """
    # If Base64 string has a prefix (e.g., "data:image/jpeg;base64,"), remove it
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    # Decode the Base64 string into binary data
    binary_data = base64.b64decode(base64_string)

    # Create a file-like object from the binary data
    file_object = BytesIO(binary_data)
    file_object.name = filename  # Set the filename attribute for the file object

    return file_object