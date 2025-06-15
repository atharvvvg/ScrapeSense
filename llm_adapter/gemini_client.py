from typing import Optional
import google.generativeai as genai
from config import settings

def get_llm_suggestion(prompt: str) -> Optional[str]:
    """
    Get a suggestion from the Gemini LLM based on the provided prompt.
    
    Args:
        prompt (str): The prompt to send to the LLM
        
    Returns:
        Optional[str]: The LLM's response text, or None if there was an error
    """
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured.")
        return None
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.LLM_MODEL_NAME)
        response = model.generate_content(prompt)
        
        # Basic check for response text, Gemini API might have specific error handling
        if response.parts:
            return response.text # response.text is a convenience accessor
        else:
            print(f"LLM Warning: Received no parts in response. Full response: {response}")
            return None

    except Exception as e:
        print(f"Error during LLM suggestion: {e}")
        return None 