def calculate_tokens(text, characters_per_token=4):
    """
    Calculate the number of tokens in the input text based on the average number of characters per token.

    Parameters:
    - text (str): The input text.
    - characters_per_token (int): Average number of characters per token (default is 4).

    Returns:
    - total_tokens (int): Total tokens for the input text.
    """
    # Count the number of characters in the input text
    num_characters = len(text)

    # Calculate the number of tokens
    total_tokens = num_characters / characters_per_token

    return int(total_tokens)


# Example usage
text = "This is an example sentence to calculate token usage."
tokens_used = calculate_tokens(text)
print(f"Tokens used: {tokens_used}")
