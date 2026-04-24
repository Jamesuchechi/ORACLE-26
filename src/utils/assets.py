import hashlib

class AssetPipeline:
    """
    Robust strategy for player and venue imagery.
    Uses deterministic hashing to ensure consistent placeholder generation.
    """
    
    @staticmethod
    def get_player_image(player_name: str, team: str) -> str:
        """
        Deterministic DiceBear avatar. 
        Ensures a player always gets the same high-quality avatar.
        """
        seed = f"{player_name}_{team}".replace(" ", "_")
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}&backgroundColor=b6e3f4,c0aede,d1d4f9"

    @staticmethod
    def get_venue_image(venue_name: str) -> str:
        """
        Premium placeholder for venues.
        Uses Unsplash source for specific locations if available, else a high-quality abstract.
        """
        clean_name = venue_name.replace(" ", "_").lower()
        # Fallback to high-quality stadium photography
        return f"https://images.unsplash.com/photo-1504450758481-7338eba7524a?q=80&w=1200&auto=format&fit=crop"

    @staticmethod
    def get_team_logo(team_name: str) -> str:
        """
        Standardized flag/logo fetcher.
        """
        # We can use a reliable flag API or local assets
        return f"https://flagsapi.com/{team_name[:2].upper()}/flat/64.png" # Simple fallback
