def calculate_openai_tokens(text):
    # Simple approximation for local development
    # Actual token count will be different from OpenAI's tokenizer
    return len(text.split())
