import os
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Load env from root
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

class ConfluxAnalyst:
    """
    The Zerve Analyst — powered by Groq (Llama 3).
    Provides real-time reasoning across the 4 vertical intelligence streams.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate_insight(self, context_data: dict, user_query: str = None) -> str:
        """
        Generates a reasoning-heavy insight based on current confluence data.
        """
        system_prompt = """
        You are the ORACLE-26 Intelligence Analyst. Your role is to provide deep, multi-modal reasoning 
        across Sports, Markets, Economics, Climate, and Social signals for the 2026 World Cup.
        
        CRITICAL: You must be factually accurate about the 48-team field. 
        If you see data that suggests a team is in the tournament when they are NOT (e.g., Nigeria, if they failed to qualify), 
        you must flag it as a data discrepancy.
        
        Your tone is professional, "Bloomberg-style" intelligence, focusing on 'Divergence' and 'Alpha'.
        """
        
        content = f"Current Intelligence Context:\n{json.dumps(context_data, indent=2)}\n\n"
        if user_query:
            content += f"User Query: {user_query}"
        else:
            content += "Task: Provide a macro-briefing on the current tournament state, highlighting the top 3 alpha opportunities."

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.2,
                max_tokens=512
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Analyst Offline: {str(e)}"

# Singleton for API use
zerve_analyst = ConfluxAnalyst()
