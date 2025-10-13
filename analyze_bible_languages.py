#!/usr/bin/env python3
"""
Bible Languages Analysis Script

This script analyzes the available Bible versions through the API.Bible service,
providing insights into language distribution, version availability, and 
comparative analysis across different languages.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import argparse
import sys
import os

# Add the backend directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.core.config import settings
    from backend.services.bible_api import BibleAPIService
except ImportError:
    # Fallback configuration if backend imports fail
    print("Warning: Could not import backend configuration. Using fallback settings.")
    
    class FallbackSettings:
        bible_api_base_url = "https://api.scripture.api.bible/v1"
        bible_api_key = os.getenv("BIBLE_API_KEY", "")
    
    settings = FallbackSettings()


class BibleLanguageAnalyzer:
    """Analyzes Bible versions and languages available through the API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with API configuration."""
        self.api_key = api_key or settings.bible_api_key
        self.base_url = settings.bible_api_base_url
        
        if not self.api_key:
            raise ValueError("Bible API key is required. Set BIBLE_API_KEY environment variable.")
        
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        self.bibles_data = []
        self.languages_data = {}
    
    def fetch_all_bibles(self) -> List[Dict]:
        """Fetch all available Bible versions from the API."""
        try:
            print("Fetching Bible versions from API...")
            response = requests.get(f"{self.base_url}/bibles", headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            self.bibles_data = data.get("data", [])
            print(f"Found {len(self.bibles_data)} Bible versions")
            return self.bibles_data
            
        except requests.RequestException as e:
            print(f"Error fetching Bible versions: {e}")
            return []
    
    def analyze_languages(self) -> Dict:
        """Analyze the distribution of Bible versions by language."""
        if not self.bibles_data:
            self.fetch_all_bibles()
        
        language_stats = defaultdict(lambda: {
            'count': 0,
            'versions': [],
            'language_info': {}
        })
        
        for bible in self.bibles_data:
            language = bible.get('language', {})
            lang_id = language.get('id', 'unknown')
            lang_name = language.get('name', 'Unknown')
            
            language_stats[lang_id]['count'] += 1
            language_stats[lang_id]['versions'].append({
                'id': bible.get('id'),
                'name': bible.get('name'),
                'abbreviation': bible.get('abbreviation', ''),
                'description': bible.get('description', '')
            })
            language_stats[lang_id]['language_info'] = {
                'name': lang_name,
                'id': lang_id
            }
        
        # Sort by count
        sorted_languages = dict(sorted(
            language_stats.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        ))
        
        return sorted_languages
    
    def get_top_languages(self, limit: int = 10) -> List[Tuple[str, Dict]]:
        """Get the top N languages by number of Bible versions."""
        language_stats = self.analyze_languages()
        return list(language_stats.items())[:limit]
    
    def analyze_english_versions(self) -> Dict:
        """Detailed analysis of English Bible versions."""
        if not self.bibles_data:
            self.fetch_all_bibles()
        
        english_versions = []
        for bible in self.bibles_data:
            if bible.get('language', {}).get('id') == 'eng':
                english_versions.append(bible)
        
        # Categorize by type (if possible from name/description)
        categories = {
            'traditional': [],
            'modern': [],
            'study': [],
            'children': [],
            'other': []
        }
        
        traditional_keywords = ['king james', 'kjv', 'authorized', 'douay']
        modern_keywords = ['niv', 'esv', 'nlt', 'nasb', 'web', 'berean', 'bsb']
        study_keywords = ['study', 'annotated', 'notes']
        children_keywords = ['children', 'kids', 'young', 'easy']
        
        for version in english_versions:
            name_lower = version.get('name', '').lower()
            desc_lower = version.get('description', '').lower()
            text = f"{name_lower} {desc_lower}"
            
            categorized = False
            
            if any(keyword in text for keyword in traditional_keywords):
                categories['traditional'].append(version)
                categorized = True
            elif any(keyword in text for keyword in modern_keywords):
                categories['modern'].append(version)
                categorized = True
            elif any(keyword in text for keyword in study_keywords):
                categories['study'].append(version)
                categorized = True
            elif any(keyword in text for keyword in children_keywords):
                categories['children'].append(version)
                categorized = True
            
            if not categorized:
                categories['other'].append(version)
        
        return {
            'total_english': len(english_versions),
            'categories': categories,
            'all_versions': english_versions
        }
    
    def find_multilingual_availability(self) -> Dict:
        """Find Bible versions available in multiple languages (same content)."""
        # This is a simplified analysis - in reality, matching would be more complex
        name_groups = defaultdict(list)
        
        for bible in self.bibles_data:
            # Group by similar names (simplified matching)
            name = bible.get('name', '').lower()
            # Remove common words that might vary by language
            clean_name = name.replace('bible', '').replace('version', '').strip()
            if clean_name:
                name_groups[clean_name].append(bible)
        
        multilingual = {}
        for name, bibles in name_groups.items():
            if len(bibles) > 1:
                languages = set()
                for bible in bibles:
                    lang_name = bible.get('language', {}).get('name', 'Unknown')
                    languages.add(lang_name)
                
                if len(languages) > 1:
                    multilingual[name] = {
                        'versions': bibles,
                        'languages': list(languages),
                        'language_count': len(languages)
                    }
        
        return multilingual
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive analysis report."""
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 80,
            "BIBLE LANGUAGES ANALYSIS REPORT",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ])
        
        # Overall statistics
        if not self.bibles_data:
            self.fetch_all_bibles()
        
        total_bibles = len(self.bibles_data)
        language_stats = self.analyze_languages()
        total_languages = len(language_stats)
        
        report_lines.extend([
            "OVERALL STATISTICS",
            "-" * 40,
            f"Total Bible Versions: {total_bibles}",
            f"Total Languages: {total_languages}",
            ""
        ])
        
        # Top languages
        report_lines.extend([
            "TOP 15 LANGUAGES BY BIBLE VERSION COUNT",
            "-" * 40
        ])
        
        top_languages = self.get_top_languages(15)
        for i, (lang_id, lang_data) in enumerate(top_languages, 1):
            lang_name = lang_data['language_info']['name']
            count = lang_data['count']
            report_lines.append(f"{i:2}. {lang_name:<30} ({lang_id:<5}): {count:3} versions")
        
        report_lines.append("")
        
        # English version analysis
        english_analysis = self.analyze_english_versions()
        report_lines.extend([
            "ENGLISH BIBLE VERSIONS ANALYSIS",
            "-" * 40,
            f"Total English Versions: {english_analysis['total_english']}",
            ""
        ])
        
        for category, versions in english_analysis['categories'].items():
            if versions:
                report_lines.append(f"{category.title()} Versions ({len(versions)}):")
                for version in versions[:5]:  # Show top 5 in each category
                    name = version.get('name', 'Unknown')
                    abbr = version.get('abbreviation', '')
                    if abbr:
                        report_lines.append(f"  - {name} ({abbr})")
                    else:
                        report_lines.append(f"  - {name}")
                if len(versions) > 5:
                    report_lines.append(f"  ... and {len(versions) - 5} more")
                report_lines.append("")
        
        # Language diversity insights
        report_lines.extend([
            "LANGUAGE DIVERSITY INSIGHTS",
            "-" * 40
        ])
        
        # Calculate some basic statistics
        version_counts = [lang_data['count'] for lang_data in language_stats.values()]
        avg_versions = sum(version_counts) / len(version_counts)
        
        single_version_langs = sum(1 for count in version_counts if count == 1)
        multiple_version_langs = sum(1 for count in version_counts if count > 1)
        
        report_lines.extend([
            f"Average versions per language: {avg_versions:.1f}",
            f"Languages with only 1 version: {single_version_langs}",
            f"Languages with multiple versions: {multiple_version_langs}",
            ""
        ])
        
        # Most translated (simplified analysis)
        multilingual = self.find_multilingual_availability()
        if multilingual:
            report_lines.extend([
                "POTENTIAL MULTILINGUAL CONTENT (TOP 10)",
                "-" * 40
            ])
            
            sorted_multilingual = sorted(
                multilingual.items(), 
                key=lambda x: x[1]['language_count'], 
                reverse=True
            )
            
            for i, (name, data) in enumerate(sorted_multilingual[:10], 1):
                lang_count = data['language_count']
                languages = ', '.join(data['languages'][:5])
                if len(data['languages']) > 5:
                    languages += f" (and {len(data['languages']) - 5} more)"
                report_lines.append(f"{i:2}. {name.title():<25} - {lang_count} languages")
                report_lines.append(f"    Languages: {languages}")
            
            report_lines.append("")
        
        # API Usage Notes
        report_lines.extend([
            "NOTES",
            "-" * 40,
            "- This analysis is based on the API.Bible service",
            "- Some Bible versions may require higher API tier access",
            "- Language matching is simplified and may not be perfectly accurate",
            "- For production use, consider caching this data to reduce API calls",
            ""
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"Report saved to: {output_file}")
            except IOError as e:
                print(f"Error saving report to file: {e}")
        
        return report_content
    
    def export_raw_data(self, output_file: str = "bible_data.json"):
        """Export raw Bible data to JSON file for further analysis."""
        if not self.bibles_data:
            self.fetch_all_bibles()
        
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_bibles': len(self.bibles_data),
                'api_source': 'api.scripture.api.bible'
            },
            'bibles': self.bibles_data,
            'language_analysis': self.analyze_languages()
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"Raw data exported to: {output_file}")
        except IOError as e:
            print(f"Error exporting data: {e}")


def main():
    """Main function to run the Bible languages analysis."""
    parser = argparse.ArgumentParser(description='Analyze Bible languages and versions')
    parser.add_argument('--output', '-o', help='Output file for the report')
    parser.add_argument('--export-json', help='Export raw data to JSON file')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top languages to show (default: 10)')
    parser.add_argument('--english-only', action='store_true', help='Focus only on English versions')
    
    args = parser.parse_args()
    
    try:
        analyzer = BibleLanguageAnalyzer()
        
        if args.english_only:
            # Quick English-only analysis
            english_analysis = analyzer.analyze_english_versions()
            print(f"\nEnglish Bible Versions Analysis:")
            print(f"Total English versions: {english_analysis['total_english']}")
            print("\nCategories:")
            for category, versions in english_analysis['categories'].items():
                if versions:
                    print(f"  {category.title()}: {len(versions)} versions")
                    for version in versions[:3]:  # Show first 3
                        print(f"    - {version.get('name', 'Unknown')}")
                    if len(versions) > 3:
                        print(f"    ... and {len(versions) - 3} more")
        else:
            # Full analysis
            report = analyzer.generate_report(args.output)
            
            if not args.output:
                print(report)
        
        # Export raw data if requested
        if args.export_json:
            analyzer.export_raw_data(args.export_json)
    
    except Exception as e:
        print(f"Error running analysis: {e}")
        if "API key" in str(e):
            print("\nTo fix this issue:")
            print("1. Get an API key from https://scripture.api.bible/")
            print("2. Set the BIBLE_API_KEY environment variable:")
            print("   export BIBLE_API_KEY='your-api-key-here'")
            print("3. Or update your backend/core/config.py file")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())