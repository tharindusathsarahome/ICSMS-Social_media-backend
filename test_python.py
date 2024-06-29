import google.generativeai as genai

genai.configure(api_key="AIzaSyAOc9Ixda9XeUddNGyqL9RRLvLpDrUZ5DU")


def get_gemini_chat():
    """
    Starts a chat session with the Gemini LLM.
    """
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    return chat


def get_gemini_response(chat, message):
    """
    Sends a message to the ongoing chat session and returns the response.
    """
    response = chat.send_message(message)
    return response.text


def identify_products(facebook_post_description):
    """
    Attempts to identify products in a Facebook post description using Gemini.

    Args:
        facebook_post_description (str): The text content of the Facebook post.

    Returns:
        str: A list of potential products found in the description.
    """

    chat = get_gemini_chat()

    message = f"This is a Facebook post description: '{facebook_post_description}'.\n Give me a ',' separated list string of products mentioned in this post. Give the mainly identified Products. Not sub Products or partially mentioned Products. And Do not provide anything else."

    response = get_gemini_response(chat, message)

    potential_products = []
    for word in response.split(","):
        if is_potentially_a_product(word):
            potential_products.append(word)

    if potential_products:
        return potential_products
    else:
        return -1


def is_potentially_a_product(word):
    print(f"Checking if '{word}' is a product...")
    return False  # Replace with your actual product identification logic



text = """Ever dreamed of building your own AI?  

Google Vertex AI makes it possible! This awesome platform lets ANYONE (yes, even you!) create cool AI tools like chatbots, image recognition, and more.  No coding experience needed!    Join the discussion: what AI will YOU build?  

#AI #VertexAI #Google #BuildYourOwnAI"""


if __name__ == "__main__":
    print(identify_products(text))