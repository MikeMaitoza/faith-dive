import requests
from typing import List, Optional, Dict, Any
from backend.core.config import settings
from backend.models.schemas import BibleVersion, VerseContent, SearchResult

class BibleAPIService:
    def __init__(self):
        self.base_url = settings.bible_api_base_url
        self.api_key = settings.bible_api_key
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_english_bibles(self) -> List[BibleVersion]:
        """Get all English Bible versions with preferred versions prioritized"""
        try:
            response = requests.get(f"{self.base_url}/bibles", headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            english_bibles = []
            preferred_bibles = []
            
            # Define preferred Bible versions based on what's actually available
            # Premium versions (NIV, NASB, NET) require higher API tier
            # Using best available free versions
            preferred_abbreviations = ['WEB', 'BSB', 'ASV', 'KJV']
            preferred_names = [
                'World English Bible',
                'Berean Standard Bible',
                'American Standard Version',
                'King James'
            ]
            
            for bible in data.get("data", []):
                # Filter for English language bibles
                if bible.get("language", {}).get("id") == "eng":
                    bible_version = BibleVersion(
                        id=bible["id"],
                        name=bible["name"],
                        language=bible["language"]["name"],
                        abbreviation=bible.get("abbreviation", ""),
                        description=bible.get("description", "")
                    )
                    
                    # Check if this is a preferred Bible version
                    is_preferred = (
                        bible_version.abbreviation in preferred_abbreviations or
                        any(pref_name.lower() in bible_version.name.lower() for pref_name in preferred_names)
                    )
                    
                    if is_preferred:
                        preferred_bibles.append(bible_version)
                    else:
                        english_bibles.append(bible_version)
            
            # Sort preferred Bibles to maintain NIV, NASB, NET order
            def sort_preferred(bible):
                for i, abbr in enumerate(preferred_abbreviations):
                    if abbr in bible.abbreviation or abbr.lower() in bible.name.lower():
                        return i
                for i, name in enumerate(preferred_names):
                    if name.lower() in bible.name.lower():
                        return i
                return 999
            
            preferred_bibles.sort(key=sort_preferred)
            
            # Return preferred Bibles first, then others alphabetically
            english_bibles.sort(key=lambda x: x.name)
            return preferred_bibles + english_bibles
            
        except requests.RequestException as e:
            print(f"Error fetching Bible versions: {e}")
            return []
    
    def search_verses(self, query: str, bible_id: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
        """Search for verses containing the query text"""
        try:
            # If no bible_id specified, use the first available English Bible (which will be preferred)
            if not bible_id:
                english_bibles = self.get_english_bibles()
                if not english_bibles:
                    print("No English Bibles available")
                    return []
                bible_id = english_bibles[0].id
                print(f"Using default Bible: {english_bibles[0].name} ({bible_id})")
            
            # Construct search URL
            search_url = f"{self.base_url}/bibles/{bible_id}/search"
            params = {
                "query": query,
                "limit": limit,
                "sort": "relevance"
            }
            
            print(f"Searching for '{query}' in Bible {bible_id}")
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            search_results = []
            
            # Get Bible info for the results
            bible_info = self.get_bible_info(bible_id)
            bible_name = bible_info.get("name", "Unknown Bible") if bible_info else "Unknown Bible"
            
            verses_data = data.get("data", {}).get("verses", [])
            print(f"Found {len(verses_data)} verses")
            
            for verse in verses_data:
                try:
                    # Handle different possible verse text fields
                    verse_text = verse.get("text", "")
                    if not verse_text:
                        verse_text = verse.get("content", "")
                    
                    search_results.append(SearchResult(
                        verse=VerseContent(
                            id=verse["id"],
                            reference=verse["reference"],
                            content=self._clean_verse_text(verse_text)
                        ),
                        bible_id=bible_id,
                        bible_name=bible_name
                    ))
                except KeyError as ke:
                    print(f"Missing required field in verse data: {ke}")
                    continue
            
            return search_results
            
        except requests.RequestException as e:
            print(f"Error searching verses: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return []
    
    def get_verse(self, verse_id: str, bible_id: str) -> Optional[VerseContent]:
        """Get a specific verse by ID"""
        try:
            response = requests.get(
                f"{self.base_url}/bibles/{bible_id}/verses/{verse_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            verse_data = data.get("data")
            
            if verse_data:
                return VerseContent(
                    id=verse_data["id"],
                    reference=verse_data["reference"],
                    content=self._clean_verse_text(verse_data["content"])
                )
            
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching verse: {e}")
            return None
    
    def get_bible_info(self, bible_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific Bible version"""
        try:
            response = requests.get(f"{self.base_url}/bibles/{bible_id}", headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("data")
            
        except requests.RequestException as e:
            print(f"Error fetching Bible info: {e}")
            return None
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean verse text by removing HTML tags and extra whitespace"""
        import re
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace and normalize
        clean_text = ' '.join(clean_text.split())
        return clean_text

# Create a singleton instance
bible_api_service = BibleAPIService()