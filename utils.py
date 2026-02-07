import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_genai():
    """Configures the Google Generative AI with the API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)

def generate_content(prompt, model_name="gemini-1.5-flash"):
    """
    Generates content using the specified Gemini model.
    
    Args:
        prompt (str): The input prompt for the model.
        model_name (str): The name of the model to use. Defaults to "gemini-1.5-flash".
        
    Returns:
        str: The generated text content.
    """
    try:
        configure_genai()
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {e}"
