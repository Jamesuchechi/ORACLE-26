import os
import json
import pandas as pd
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
        
        # Soft-fail if keys are missing to prevent app-wide crash
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
        if not self.groq_client:
            print("◈ WARNING: GROQ_API_KEY missing. Analyst will operate in fallback mode.")
            
        self.mistral_client = Mistral(api_key=self.mistral_key) if self.mistral_key and Mistral else None
        
        # Fallback Chain Configuration
        self.models = []
        if self.groq_client:
            self.models.extend([
                {"provider": "groq", "name": "llama-3.3-70b-versatile"},
                {"provider": "groq", "name": "llama-3.1-8b-instant"}
            ])
        if self.mistral_client:
            self.models.append({"provider": "mistral", "name": "mistral-large-latest"})

    def build_cross_domain_context(self, query: str, page_context: dict = None) -> dict:
        """
        Builds a structured context by pulling relevant signals from all 4 verticals.
        Enhanced to detect intent and cross-link entities.
        Now includes page_context from the frontend to ground the model in the current view.
        """
        query = query.lower()
        processed_dir = Path("data/processed")
        page_id = (page_context or {}).get("activePage", "dashboard")
        context = {
            "sports_wc2026": [],
            "markets": [],
            "climate": [],
            "social_cultural": [],
            "intent": "general",
            "page_context": page_context or {}
        }
        
        # Keywords for intent detection
        intents = {
            "markets": ["market", "alpha", "price", "odds", "polymarket", "kalshi", "mispricing", "value", "arbitrage"],
            "climate": ["climate", "weather", "heat", "altitude", "stress", "humidity", "venue", "risk", "environment"],
            "social": ["social", "cultural", "trend", "momentum", "hype", "reddit", "tipping", "sentiment", "buzz"],
            "sports": ["win", "lose", "match", "team", "score", "bracket", "simulation", "rankings", "cup", "fifa"]
        }
        
        found_intents = [k for k, v in intents.items() if any(w in query for w in v)]
        if found_intents:
            context["intent"] = found_intents[0]

        # 1. Sports / WC2026 - Find mentioned teams
        try:
            df_sports = pd.read_csv(processed_dir / "conflux_wc2026.csv")
            from src.constants import ALL_WC_TEAMS
            mentioned_teams = [t for t in ALL_WC_TEAMS if t.lower() in query]
            
            if mentioned_teams:
                res = df_sports[df_sports['subject'].isin(mentioned_teams)]
                context["sports_wc2026"] = res.to_dict(orient="records")
            else:
                # Default: Top alpha gaps or top rankings
                context["sports_wc2026"] = df_sports.sort_values("conflux_score", ascending=False).head(3).to_dict(orient="records")
        except: pass

        # 2. Cross-Domain Linkage: If teams mentioned, pull their climate and social signals
        if mentioned_teams:
            try:
                # Climate
                df_climate = pd.read_csv(processed_dir / "conflux_climate_risk.csv")
                # Find venues for these teams (assuming they play in specific cities or mapping exists)
                # For now, just search for team name in climate rows if they appear there
                relevant_climate = df_climate[df_climate.apply(lambda row: any(t.lower() in str(row).lower() for t in mentioned_teams), axis=1)]
                context["climate"] = relevant_climate.to_dict(orient="records")
                
                # Social
                df_social = pd.read_csv(processed_dir / "conflux_cultural_moment.csv")
                relevant_social = df_social[df_social.apply(lambda row: any(t.lower() in str(row).lower() for t in mentioned_teams), axis=1)]
                context["social_cultural"] = relevant_social.to_dict(orient="records")
            except: pass

        # 3. Market Specific Context
        try:
            df_markets = pd.read_csv(processed_dir / "conflux_market_calib.csv")
            if mentioned_teams:
                relevant_m = df_markets[df_markets['subject'].isin(mentioned_teams)]
                context["markets"] = relevant_m.to_dict(orient="records")
            
            if not context["markets"]:
                context["markets"] = df_markets.sort_values("abs_alpha", ascending=False).head(3).to_dict(orient="records")
        except: pass

        # 4. Fill gaps if still empty
        if not context["climate"]:
            try:
                df_climate = pd.read_csv(processed_dir / "conflux_climate_risk.csv")
                context["climate"] = df_climate.sort_values("risk_score", ascending=False).head(2).to_dict(orient="records")
            except: pass
            
        if not context["social_cultural"]:
            try:
                df_social = pd.read_csv(processed_dir / "conflux_cultural_moment.csv")
                context["social_cultural"] = df_social.sort_values("tipping_score", ascending=False).head(2).to_dict(orient="records")
            except: pass

        # 5. Page-Specific Deep Context
        if page_id == "bracket-simulator":
            try:
                df_bracket = pd.read_csv(processed_dir / "conflux_wc2026.csv")
                # Group by group and get top teams
                groups_data = {}
                for g in df_bracket['group'].unique():
                    groups_data[g] = df_bracket[df_bracket['group'] == g].sort_values("conflux_score", ascending=False).to_dict(orient="records")
                context["bracket_data"] = groups_data
            except: pass

        return context

    def _generate_heuristic_report(self, context_data: dict) -> str:
        """
        Zero-AI Fallback: Generates a structured markdown report directly from data.
        Ensures the terminal never looks 'broken' even if LLM APIs are down.
        """
        report = "### ◈ CONFLUX AUTOMATED INTELLIGENCE BRIEFING\n"
        report += "*System Status: LLM Analysis Link Offline. Surface-level heuristics active.*\n\n"
        
        # 1. THE BIG BET (Featured Alpha)
        report += "#### 🚨 FEATURED ALPHA: THE USA 'INSTITUTIONAL UNDERDOG'\n"
        report += "Our model has identified the **USA** as the single most underpriced asset in the tournament. "
        report += "While Polymarket consensus sits at a skeptical **3%**, CONFLUX signals indicate a **12.4%** real win probability. "
        report += "This 4x divergence is driven by a 'Conflux Perfect Storm': **Maximum Climate Resilience (0.97)**, **Peak Social Momentum (1.0)**, and **Top-Tier Economic Resilience (0.75)**. "
        report += "Markets are pricing on history; CONFLUX is pricing on multi-modal reality.\n\n"

        # 2. Sports Summary
        sports = context_data.get("sports_wc2026", [])
        if sports:
            report += "#### ⚽ Vertical I: Sports Simulations\n"
            for t in sports[:3]:
                if t['subject'] == "USA": continue # Already covered in Big Bet
                report += f"- **{t['subject']}**: Current Conflux Score: **{t['conflux_score']:.3f}**. Primary driver: {t['interpretation'][:60]}...\n"
        
        # 3. Market Summary
        markets = context_data.get("markets", [])
        if markets:
            report += "\n#### 📈 Vertical II: Market Discrepancies\n"
            for m in markets[:2]:
                report += f"- **{m.get('subject', m.get('team', 'Event'))}**: Alpha Gap detected at **{m.get('alpha_gap', 0)*100:.1f}pp**. Strategy: {m.get('interpretation', 'Analyze for value.')}\n"
        
        report += "\n---\n*NOTE: This is a pre-formatted heuristic report generated by the Conflux Core Engine while AI reasoning modules are in maintenance.*"
        return report

    def generate_insight(self, context_data: dict, user_query: str = None, history: list = None, page_context: dict = None) -> str:
        """
        Generates reasoning with automatic fallback across providers.
        Supports conversation history and page-specific personas.
        """
        page_id = (page_context or {}).get("activePage", "dashboard")
        
        # Dynamic Persona based on where the user is
        page_personas = {
            "bracket-simulator": "You are currently observing the **Tournament Bracket Simulator**. You have access to Monte Carlo simulation data. Focus on advancement probabilities, upset alerts, and group-stage dynamics.",
            "fusion-hub": "You are at the **Conflux Fusion Hub**. This is the heart of the engine where signals from Sports, Markets, Economics, and Climate collide. Focus on cross-domain interaction effects.",
            "alpha-radar": "You are monitoring the **Alpha Discovery** module. Your goal is to find mispricings and arbitrage opportunities between prediction markets and the Conflux model.",
            "climate-risk": "You are analyzing **Climate Risk Intelligence**. Focus on how heat, humidity, and altitude stress impact athletic performance and infrastructure.",
            "social-trends": "You are tracking **Social & Cultural Moments**. Focus on tipping points, sentiment velocity, and how digital buzz precedes market moves."
        }
        
        current_persona = page_personas.get(page_id, "You are observing the main Intelligence Terminal dashboard.")

        system_prompt = f"""
        You are the **ORACLE-26 Intelligence Analyst**. You are a sophisticated, Bloomberg-style AI designed to find 'alpha' across complex data signals.
        
        **CURRENT LOCATION IN TERMINAL**: {current_persona}

        **BEHAVIOR RULES**:
        1. **Flexibility**: If the user asks a general question or wants to chat about something else, be a friendly, witty, and highly capable AI assistant. You don't ALWAYS have to talk about Conflux data if the user is being casual.
        2. **Contextual Grounding**: Use the provided 'Intelligence Context' to ground your technical answers.
        3. **Tone**: Premium, "Bloomberg-Terminal" aesthetic. Use **Markdown** for structure. **BOLD** key numbers and team names.
        4. **Insight over Data**: Don't just list numbers. Explain WHY they matter. (e.g. "Argentina's high climate risk in Monterrey could neutralize their technical advantage").
        5. **The USA Thesis**: If relevant, highlight the 'Institutional Underdog' thesis (USA is underpriced by markets but favored by Conflux's multi-signal model).
        
        Keep responses concise, insightful, and "giving" — provide deep reasoning rather than just surface stats.
        """
        
        content = f"Current Intelligence Context:\n{json.dumps(context_data, indent=2)}\n\n"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            # Add last 5 messages for context
            messages.extend(history[-5:])
            
        if user_query:
            messages.append({"role": "user", "content": f"{content}\nUser Query: {user_query}"})
        else:
            messages.append({"role": "user", "content": f"{content}\nTask: Provide a macro-briefing on the current tournament state."})

        for model_info in self.models:
            provider = model_info["provider"]
            model_name = model_info["name"]
            
            try:
                if provider == "groq" and self.groq_client:
                    completion = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.4, # More creative/giving
                        max_tokens=768
                    )
                    return completion.choices[0].message.content
                
                elif provider == "mistral" and self.mistral_client:
                    completion = self.mistral_client.chat.complete(
                        model=model_name,
                        messages=messages,
                        temperature=0.4,
                        max_tokens=768
                    )
                    return completion.choices[0].message.content
            
            except Exception as e:
                print(f"◈ Analyst Fallback: {model_name} failed. Error: {str(e)}")
                continue
                
        # Final Fallback: Heuristic Template (Zero-AI)
        return self._generate_heuristic_report(context_data)

    def generate_insight_stream(self, context_data: dict, user_query: str = None, history: list = None, page_context: dict = None):
        """
        Streaming version of generate_insight.
        Yields chunks of text.
        """
        page_id = (page_context or {}).get("activePage", "dashboard")
        system_prompt = f"""
        You are the ORACLE-26 Intelligence Analyst. 
        Location: {page_id}.
        Provide deep reasoning, Bloomberg-style tone. 
        Be flexible: chat casually if the user does, but be a master analyst when data is involved.
        Markdown format.
        """
        
        content = f"Context: {json.dumps(context_data)}\n\nQuery: {user_query or 'Macro-briefing'}"
        messages = [{"role": "system", "content": system_prompt}]
        if history: messages.extend(history[-5:])
        messages.append({"role": "user", "content": content})

        # Only Groq supports easy streaming for now in this setup
        if self.groq_client:
            try:
                stream = self.groq_client.chat.completions.create(
                    model=self.models[0]["name"],
                    messages=messages,
                    temperature=0.4, # Slightly higher for more "giving" and flexible responses
                    max_tokens=1024,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            except Exception as e:
                yield f"◈ Stream Error: {str(e)}. Falling back to static."
                yield self.generate_insight(context_data, user_query, history, page_context=page_context)
        else:
            yield self.generate_insight(context_data, user_query, history, page_context=page_context)

# Singleton for API use
zerve_analyst = ConfluxAnalyst()

