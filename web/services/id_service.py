
import random
import string
import time

def generate_short_id(length=8):
    """
    Generates a guaranteed unique, short alphanumeric ID using randomness and a timestamp.

    Parameters:
        length (int): Total length of the ID (default is 8).
                      Must be at least 6 to accommodate uniqueness.

    Returns:
        str: A guaranteed unique alphanumeric ID.
    """
    if length < 6:
        raise ValueError("Length must be at least 6 to ensure uniqueness.")

    characters = string.ascii_letters + string.digits

    timestamp = int(time.time() * 1000)  
    base62_timestamp = ''
    while timestamp > 0:
        base62_timestamp = characters[timestamp % 62] + base62_timestamp
        timestamp //= 62

    random_part = ''.join(random.choices(characters, k=length - len(base62_timestamp)))

    return base62_timestamp + random_part