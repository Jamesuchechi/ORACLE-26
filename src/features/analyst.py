import os
import json
from groq import Groq
try:
    from mistralai import Mistral
except ImportError:
    Mistral = None

from dotenv import load_dotenv
from pathlib import Path

# Load env from root
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

class ConfluxAnalyst:
    """
    The Zerve Analyst — powered by Groq and Mistral.
    Implements a multi-model fallback chain to ensure high availability.
    """
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY not found in environment.")
        
        self.groq_client = Groq(api_key=self.groq_key)
        self.mistral_client = Mistral(api_key=self.mistral_key) if self.mistral_key and Mistral else None
        
        # Fallback Chain Configuration
        self.models = [
            {"provider": "groq", "name": "llama-3.3-70b-versatile"},
            {"provider": "groq", "name": "llama-3.1-8b-instant"},
            {"provider": "mistral", "name": "mistral-large-latest"}
        ]

    def generate_insight(self, context_data: dict, user_query: str = None) -> str:
        """
        Generates reasoning with automatic fallback across providers.
        """
        system_prompt = """
        You are the ORACLE-26 Intelligence Analyst. Provide deep, multi-modal reasoning 
        across Sports, Markets, Economics, Climate, and Social signals.
        
        FORMATTING RULES:
        1. Use **Markdown** for all responses.
        2. **BOLD** all team names, scores, and specific signal values.
        3. Use bullet points for key takeaways.
        4. Maintain a "Bloomberg-style" premium intelligence tone.
        5. Keep responses concise and scannable.
        """
        
        content = f"Current Intelligence Context:\n{json.dumps(context_data, indent=2)}\n\n"
        if user_query:
            content += f"User Query: {user_query}"
        else:
            content += "Task: Provide a macro-briefing on the current tournament state."

        last_error = ""
        for model_info in self.models:
            provider = model_info["provider"]
            model_name = model_info["name"]
            
            try:
                if provider == "groq":
                    completion = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": content}
                        ],
                        temperature=0.2,
                        max_tokens=512
                    )
                    return completion.choices[0].message.content
                
                elif provider == "mistral" and self.mistral_client:
                    completion = self.mistral_client.chat.complete(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": content}
                        ],
                        temperature=0.2,
                        max_tokens=512
                    )
                    return completion.choices[0].message.content
            
            except Exception as e:
                print(f"◈ Analyst Fallback: {model_name} failed. Error: {str(e)}")
                last_error = str(e)
                continue
                
        return f"Analyst Offline: All models in fallback chain exhausted. Last error: {last_error}"

# Singleton for API use
zerve_analyst = ConfluxAnalyst()
