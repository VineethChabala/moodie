import json
from google import genai
from google.genai import types
from lb_scrapper import Scraper
import streamlit as st

class VibeChecker():
    def __init__(self):
        self.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        self.scraper = Scraper()

    def check_vibe(self, movie_name):
        reviews = self.scraper.scrape_review(movie_name)
        system_prompt = """
    You are an expert Film Psychologist. Read the provided audience reviews.
    Your job is to determine the TRUE emotional consensus of the movie, ignoring its official genre.
    
    You MUST output your response in valid JSON format with exactly these three keys:
    - "primary_emotion": (A single word describing the main feeling, e.g., "Stressful", "Melancholic", "Joyful")
    - "warning": (A short 1-sentence warning for the viewer based on the reviews, or null if none)
    - "consensus": (A 1-2 sentence summary of the general vibe)
    """
        user_prompt = f"Movie: {movie_name}\nReviews:\n{reviews}"
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                )
            )
            result_dict = json.loads(response.text)
            return result_dict
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            return None


if __name__ == "__main__":
    checker = VibeChecker()
    print(checker.check_vibe("The Dark Knight"))
