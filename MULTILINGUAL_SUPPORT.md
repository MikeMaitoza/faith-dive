# Multilingual Bible Support

This document describes the multilingual Bible support added to Faith Dive.

## Supported Languages

The application now supports Bible versions in the following languages:

- **English** (eng) - Primary language with preferred versions (WEB, BSB, ASV, KJV)
- **Spanish** (spa)
- **Portuguese** (por)
- **French** (fra)
- **German** (deu)
- **Norwegian** (nor)
- **Swedish** (swe)
- **Finnish** (fin)
- **Greek** (ell)
- **Belarussian** (bel)
- **Ukrainian** (ukr)
- **Polish** (pol)
- **Estonian** (est)
- **Latvian** (lav)
- **Lithuanian** (lit)
- **Dutch** (nld)
- **Mandarin Chinese** (cmn)
- **Urdu** (urd)
- **Hebrew** (heb)
- **Czech** (ces)
- **Indonesian** (ind)
- **Swahili** (swa)
- **Turkish** (tur)
- **Arabic** (ara)
- **Kurdish** (ckb)
- **Haitian Creole** (hat)
- **Hungarian** (hun)
- **Icelandic** (isl)
- **Italian** (ita)
- **Romanian** (ron)
- **Nepali** (nep)
- **Cape Verdean Creole** (kab)
- **K'iche'** (quc)
- **Slovak** (slk)
- **Tonga** (ton)
- **Japanese** (jpn)
- **Yiddish** (yid)
- **Thai** (tha)
- **Hindi** (hin)
- **Bengali** (ben)
- **Vietnamese** (vie)
- **Serbian** (srp)
- **Malaysian** (msa)
- **Punjabi** (pan)
- **Persian** (fas)

## API Endpoints

### Get All Supported Bible Versions
```
GET /api/v1/bibles
```
Returns all Bible versions in supported languages, organized with English first, then other languages in priority order.

### Get English Bible Versions Only (Backward Compatibility)
```
GET /api/v1/bibles/english
```
Returns only English Bible versions with preferred versions prioritized.

### Get Bible Versions by Language
```
GET /api/v1/bibles/language/{language_id}
```
Returns Bible versions for a specific language (e.g., `/api/v1/bibles/language/spa` for Spanish).

## Frontend Changes

### Bible Version Dropdown
The Bible version dropdown in the frontend now organizes versions by language groups using `<optgroup>` elements:

```
English
  ├─ World English Bible (WEB)
  ├─ Berean Standard Bible (BSB)
  └─ ...
Spanish
  ├─ Reina Valera 1960
  └─ ...
Portuguese
  ├─ Almeida Revista e Atualizada
  └─ ...
```

### Search Functionality
- Search works with any supported Bible version
- If no Bible version is selected, the system defaults to the first available Bible (preferring English versions)
- Search results display the Bible version name and language

## Backend Implementation

### BibleAPIService Methods

- `get_supported_languages()`: Returns mapping of language codes to names
- `get_all_supported_bibles()`: Returns all Bible versions in supported languages
- `get_bibles_by_language(language_id)`: Returns Bibles for a specific language
- `get_english_bibles()`: Returns English Bibles (for backward compatibility)

### Language Priority
Languages are ordered by priority:
1. English (with preferred versions first)
2. Spanish, Portuguese, French, German
3. Nordic languages (Norwegian, Swedish, Finnish)
4. Other European languages
5. Asian languages
6. Other world languages

## Usage Examples

### Searching in Spanish
1. Select a Spanish Bible version from the dropdown
2. Enter search terms in Spanish
3. Results will be returned from the selected Spanish Bible

### Journal Entries
- Journal entries can be created from verses in any supported language
- The Bible version and language are stored with each entry
- Mixed-language journal collections are supported

### Favorites
- Favorite verses can be from any supported Bible version
- Language information is preserved with each favorite

## Notes

- Bible version availability depends on the API.Bible service
- Some languages may have limited Bible versions available
- Premium Bible versions may require higher API tier access
- The system gracefully handles missing or unavailable Bible versions

## Testing Multilingual Support

To test with a specific language:

```bash
# Get Spanish Bible versions
curl http://localhost:8000/api/v1/bibles/language/spa

# Search in a Spanish Bible
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "amor", "bible_id": "spa-bible-id", "limit": 5}'
```