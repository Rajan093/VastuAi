import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types


class GeminiClient:
    
    # Gemini model for text generation
    MODEL_NAME = "gemini-3-flash-preview"
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. "
                "Set GEMINI_API_KEY in .env or pass as argument."
            )
        
        self.client = genai.Client(api_key=self.api_key)
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 1.0,
    ) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                )
            )
            # print(response.text)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error generating response from Gemini: {str(e)}")
    
    def generate_summary(
        self,
        rules: List[Dict],
        chart: Dict[str, int],
        aspects: List[str] = ["Health", "Education", "Wealth", "Marriage"]
    ) -> Dict[str, str]:
        from .prompt_builder import PromptBuilder
        
        # Build the prompt
        prompt = PromptBuilder.build_summary_prompt(rules, chart, aspects)
        
        # Generate response
        response = self.generate_response(prompt, temperature=1.0) 
        # Parse response into aspects
        summaries = PromptBuilder.parse_summary_response(response, aspects)
        
        return summaries
