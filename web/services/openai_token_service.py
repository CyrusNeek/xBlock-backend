import tiktoken 

def calculate_openai_tokens(text, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)  

    num_tokens = len(encoding.encode(text))
    return num_tokens
