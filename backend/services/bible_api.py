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
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get mapping of supported language codes to language names"""
        return {
            'eng': 'English',
            'spa': 'Spanish', 
            'por': 'Portuguese',
            'fra': 'French',
            'deu': 'German',
            'nor': 'Norwegian',
            'swe': 'Swedish',
            'fin': 'Finnish',
            'ell': 'Greek',
            'bel': 'Belarussian',
            'ukr': 'Ukrainian',
            'pol': 'Polish',
            'est': 'Estonian',
            'lav': 'Latvian',
            'lit': 'Lithuanian',
            'nld': 'Dutch',
            'cmn': 'Mandarin Chinese',
            'urd': 'Urdu',
            'heb': 'Hebrew',
            'ces': 'Czech',
            'ind': 'Indonesian',
            'swa': 'Swahili',
            'tur': 'Turkish',
            'ara': 'Arabic',
            'ckb': 'Kurdish',
            'hat': 'Haitian Creole',
            'hun': 'Hungarian',
            'isl': 'Icelandic',
            'ita': 'Italian',
            'ron': 'Romanian',
            'nep': 'Nepali',
            'kab': 'Cape Verdean Creole',
            'quc': "K'iche'",
            'slk': 'Slovak',
            'ton': 'Tonga',
            'jpn': 'Japanese',
            'yid': 'Yiddish',
            'tha': 'Thai',
            'hin': 'Hindi',
            'ben': 'Bengali',
            'vie': 'Vietnamese',
            'srp': 'Serbian',
            'msa': 'Malaysian',
            'pan': 'Punjabi',
            'fas': 'Persian',
        }
    
    def get_english_bibles(self) -> List[BibleVersion]:
        """Get all English Bible versions with preferred versions prioritized"""
        return self.get_bibles_by_language('eng')
    
    def get_all_supported_bibles(self) -> List[BibleVersion]:
        """Get all Bible versions in supported languages, organized by preference"""
        try:
            response = requests.get(f"{self.base_url}/bibles", headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            supported_languages = self.get_supported_languages()
            
            # Organize bibles by language with English first
            language_priority = ['eng', 'spa', 'por', 'fra', 'deu', 'nor', 'swe', 'fin', 'ell', 'bel', 'ukr', 'pol', 'est', 'lav', 'lit', 'nld', 'cmn', 'urd', 'heb', 'ces', 'ind', 'swa', 'tur', 'ara', 'ckb', 'hat', 'hun', 'isl', 'ita', 'ron', 'nep', 'kab', 'quc', 'slk', 'ton', 'jpn', 'yid', 'tha', 'hin', 'ben', 'vie', 'srp', 'msa', 'pan', 'fas']
            
            bibles_by_language = {lang: [] for lang in supported_languages.keys()}
            
            for bible in data.get("data", []):
                lang_id = bible.get("language", {}).get("id", "")
                
                # Only include supported languages
                if lang_id in supported_languages:
                    bible_version = BibleVersion(
                        id=bible["id"],
                        name=bible["name"],
                        language=bible["language"]["name"],
                        abbreviation=bible.get("abbreviation", ""),
                        description=bible.get("description", "")
                    )
                    bibles_by_language[lang_id].append(bible_version)
            
            # Sort bibles within each language and compile final list
            all_bibles = []
            
            # Handle English first with preferred ordering
            if bibles_by_language['eng']:
                english_bibles = self._sort_english_bibles(bibles_by_language['eng'])
                all_bibles.extend(english_bibles)
            
            # Add other languages in priority order
            for lang_id in language_priority[1:]:  # Skip English as it's already added
                if bibles_by_language[lang_id]:
                    # Sort alphabetically within language
                    bibles_by_language[lang_id].sort(key=lambda x: x.name)
                    all_bibles.extend(bibles_by_language[lang_id])
            
            return all_bibles
            
        except requests.RequestException as e:
            print(f"Error fetching Bible versions: {e}")
            return []
    
    def get_bibles_by_language(self, language_id: str) -> List[BibleVersion]:
        """Get Bible versions for a specific language"""
        try:
            response = requests.get(f"{self.base_url}/bibles", headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            language_bibles = []
            
            for bible in data.get("data", []):
                if bible.get("language", {}).get("id") == language_id:
                    bible_version = BibleVersion(
                        id=bible["id"],
                        name=bible["name"],
                        language=bible["language"]["name"],
                        abbreviation=bible.get("abbreviation", ""),
                        description=bible.get("description", "")
                    )
                    language_bibles.append(bible_version)
            
            # Special handling for English with preferred ordering
            if language_id == 'eng':
                return self._sort_english_bibles(language_bibles)
            else:
                # Sort alphabetically for other languages
                language_bibles.sort(key=lambda x: x.name)
                return language_bibles
            
        except requests.RequestException as e:
            print(f"Error fetching {language_id} Bible versions: {e}")
            return []
    
    def _sort_english_bibles(self, english_bibles: List[BibleVersion]) -> List[BibleVersion]:
        """Sort English bibles with preferred versions first"""
        preferred_bibles = []
        other_bibles = []
        
        # Define preferred Bible versions based on what's actually available
        preferred_abbreviations = ['WEB', 'BSB', 'ASV', 'KJV']
        preferred_names = [
            'World English Bible',
            'Berean Standard Bible',
            'American Standard Version',
            'King James'
        ]
        
        for bible_version in english_bibles:
            # Check if this is a preferred Bible version
            is_preferred = (
                bible_version.abbreviation in preferred_abbreviations or
                any(pref_name.lower() in bible_version.name.lower() for pref_name in preferred_names)
            )
            
            if is_preferred:
                preferred_bibles.append(bible_version)
            else:
                other_bibles.append(bible_version)
        
        # Sort preferred Bibles to maintain priority order
        def sort_preferred(bible):
            for i, abbr in enumerate(preferred_abbreviations):
                if abbr in bible.abbreviation or abbr.lower() in bible.name.lower():
                    return i
            for i, name in enumerate(preferred_names):
                if name.lower() in bible.name.lower():
                    return i
            return 999
        
        preferred_bibles.sort(key=sort_preferred)
        other_bibles.sort(key=lambda x: x.name)
        
        return preferred_bibles + other_bibles
    
    def search_verses(self, query: str, bible_id: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
        """Search for verses containing the query text or by verse reference"""
        try:
            # If no bible_id specified, use the first available Bible (preferred English first)
            if not bible_id:
                all_bibles = self.get_all_supported_bibles()
                if not all_bibles:
                    print("No Bibles available")
                    return []
                bible_id = all_bibles[0].id
                print(f"Using default Bible: {all_bibles[0].name} ({bible_id})")
            
            # Check if this looks like a verse reference
            if self._is_verse_reference(query):
                print(f"Detected verse reference: '{query}'")
                
                # Try to get the specific verse using structured approach
                verse_result = self._search_specific_verse(query, bible_id)
                if verse_result:
                    return [verse_result]
                
                # If specific verse search fails, try keyword-based approach
                print(f"Specific verse search failed, trying keyword approach...")
                return self._search_verse_by_keywords(query, bible_id, limit)
            else:
                # For non-verse reference queries, use normal search
                return self._perform_search(query, bible_id, limit)
            
        except requests.RequestException as e:
            print(f"Error searching verses: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return []
    
    def _perform_search(self, query: str, bible_id: str, limit: int) -> List[SearchResult]:
        """Perform the actual search API call"""
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
    
    def _is_verse_reference(self, query: str) -> bool:
        """Check if the query looks like a verse reference"""
        import re
        # Common verse reference patterns
        patterns = [
            r'^\d*\s*\w+\s+\d+:\d+',  # John 3:16, 1 John 3:16
            r'^\w+\s+\d+:\d+',        # John 3:16
            r'^\d*\s*\w+\s+\d+',      # John 3, 1 John 3
            r'^\w+\s+\d+$',           # John 3
        ]
        
        for pattern in patterns:
            if re.match(pattern, query.strip(), re.IGNORECASE):
                return True
        return False
    
    
    def _search_specific_verse(self, query: str, bible_id: str) -> Optional[SearchResult]:
        """Search for a specific verse using book/chapter/verse structure"""
        try:
            book_name, chapter, verse = self._parse_verse_reference(query)
            if not all([book_name, chapter, verse]):
                return None
            
            # Get the book ID
            book_id = self._get_book_id(bible_id, book_name)
            if not book_id:
                print(f"Could not find book: {book_name}")
                return None
            
            # Construct the verse ID
            verse_id = f"{book_id}.{chapter}.{verse}"
            print(f"Trying verse ID: {verse_id}")
            
            # Try to get the verse directly
            verse_content = self.get_verse(verse_id, bible_id)
            if verse_content:
                bible_info = self.get_bible_info(bible_id)
                bible_name = bible_info.get("name", "Unknown Bible") if bible_info else "Unknown Bible"
                
                return SearchResult(
                    verse=verse_content,
                    bible_id=bible_id,
                    bible_name=bible_name
                )
            
        except Exception as e:
            print(f"Error in specific verse search: {e}")
        
        return None
    
    def _search_verse_by_keywords(self, query: str, bible_id: str, limit: int) -> List[SearchResult]:
        """Search for verses by using known keywords for famous verses"""
        # Map famous verse references to their key phrases
        verse_keywords = {
            "john 3:16": ["God so loved the world", "For God so loved", "only begotten"],
            "psalm 23:1": ["Lord is my shepherd", "shepherd I shall not want"],
            "romans 3:23": ["all have sinned", "fall short of the glory"],
            "ephesians 2:8": ["saved by grace", "grace through faith"],
            "philippians 4:13": ["can do all things", "strengthens me"],
            "1 corinthians 13:4": ["love is patient", "love is kind"],
            "matthew 28:19": ["baptizing them in the name", "Great Commission"],
            "john 14:6": ["I am the way", "way truth and life"],
            "romans 8:28": ["all things work together", "work together for good"],
            "jeremiah 29:11": ["plans to prosper", "plans for welfare"],
        }
        
        query_lower = query.lower().strip()
        
        # Find matching keywords
        for verse_ref, keywords in verse_keywords.items():
            if query_lower == verse_ref or query_lower.replace(":", " ") in verse_ref:
                print(f"Using keywords for {verse_ref}: {keywords}")
                
                for keyword in keywords:
                    results = self._perform_search(keyword, bible_id, 1)
                    if results:
                        print(f"Found verse using keyword: '{keyword}'")
                        return results
        
        # If no specific keywords found, try the book name
        book_name = self._extract_book_name(query)
        if book_name:
            print(f"Searching for book name: {book_name}")
            return self._perform_search(book_name, bible_id, limit)
        
        return []
    
    def _parse_verse_reference(self, query: str) -> tuple:
        """Parse a verse reference like 'John 3:16' into components"""
        import re
        
        # Handle various formats
        patterns = [
            r'^(\d*\s*\w+)\s+(\d+):(\d+)$',  # John 3:16, 1 John 3:16
            r'^(\w+)\s+(\d+):(\d+)$',        # John 3:16
        ]
        
        for pattern in patterns:
            match = re.match(pattern, query.strip(), re.IGNORECASE)
            if match:
                book_name = match.group(1).strip()
                chapter = match.group(2)
                verse = match.group(3)
                return book_name, chapter, verse
        
        return None, None, None
    
    def _get_book_id(self, bible_id: str, book_name: str) -> Optional[str]:
        """Get the book ID for a given book name"""
        try:
            response = requests.get(f"{self.base_url}/bibles/{bible_id}/books", headers=self.headers)
            if response.status_code != 200:
                return None
            
            books = response.json().get("data", [])
            book_name_lower = book_name.lower().strip()
            
            # Direct name match
            for book in books:
                if book.get("name", "").lower().strip() == book_name_lower:
                    return book.get("id")
            
            # Partial name match
            for book in books:
                if book_name_lower in book.get("name", "").lower():
                    return book.get("id")
            
            # Common abbreviations
            abbreviations = {
                "john": "JHN",
                "matthew": "MAT",
                "mark": "MRK",
                "luke": "LUK",
                "acts": "ACT",
                "romans": "ROM",
                "1 corinthians": "1CO",
                "2 corinthians": "2CO",
                "galatians": "GAL",
                "ephesians": "EPH",
                "philippians": "PHP",
                "colossians": "COL",
                "1 thessalonians": "1TH",
                "2 thessalonians": "2TH",
                "1 timothy": "1TI",
                "2 timothy": "2TI",
                "titus": "TIT",
                "philemon": "PHM",
                "hebrews": "HEB",
                "james": "JAS",
                "1 peter": "1PE",
                "2 peter": "2PE",
                "1 john": "1JN",
                "2 john": "2JN",
                "3 john": "3JN",
                "jude": "JUD",
                "revelation": "REV",
                "genesis": "GEN",
                "exodus": "EXO",
                "leviticus": "LEV",
                "numbers": "NUM",
                "deuteronomy": "DEU",
                "joshua": "JOS",
                "judges": "JDG",
                "ruth": "RUT",
                "1 samuel": "1SA",
                "2 samuel": "2SA",
                "1 kings": "1KI",
                "2 kings": "2KI",
                "1 chronicles": "1CH",
                "2 chronicles": "2CH",
                "ezra": "EZR",
                "nehemiah": "NEH",
                "esther": "EST",
                "job": "JOB",
                "psalm": "PSA",
                "psalms": "PSA",
                "proverbs": "PRO",
                "ecclesiastes": "ECC",
                "song of solomon": "SOS",
                "isaiah": "ISA",
                "jeremiah": "JER",
                "lamentations": "LAM",
                "ezekiel": "EZK",
                "daniel": "DAN",
                "hosea": "HOS",
                "joel": "JOL",
                "amos": "AMO",
                "obadiah": "OBA",
                "jonah": "JON",
                "micah": "MIC",
                "nahum": "NAM",
                "habakkuk": "HAB",
                "zephaniah": "ZEP",
                "haggai": "HAG",
                "zechariah": "ZEC",
                "malachi": "MAL",
            }
            
            abbr = abbreviations.get(book_name_lower)
            if abbr:
                for book in books:
                    if book.get("id") == abbr:
                        return abbr
            
        except Exception as e:
            print(f"Error getting book ID: {e}")
        
        return None
    
    def _extract_book_name(self, query: str) -> Optional[str]:
        """Extract book name from a verse reference"""
        import re
        
        match = re.match(r'^(\d*\s*\w+)', query.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
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