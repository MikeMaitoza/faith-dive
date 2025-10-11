# Database Fixes

## Fix: NULL Timestamp Fields (2025-10-11)

### Problem
- Journal entries and favorite verses had NULL values for `created_at` and `updated_at` timestamps
- This caused FastAPI ResponseValidationError when trying to serialize API responses
- API endpoints `/api/v1/journal` and `/api/v1/favorites` were returning 500 Internal Server Error

### Root Cause
Existing data was created before SQLAlchemy `server_default=func.now()` was properly configured, resulting in NULL timestamp fields.

### Solution Applied
Updated all NULL timestamp fields in the database:

```sql
-- Fix journal entries
UPDATE journal_entries SET 
  created_at = datetime('now'), 
  updated_at = datetime('now') 
WHERE created_at IS NULL OR updated_at IS NULL;

-- Fix favorite verses  
UPDATE favorite_verses SET 
  created_at = datetime('now') 
WHERE created_at IS NULL;
```

### Verification
- ✅ `/api/v1/journal` endpoint now returns 3 journal entries with proper timestamps
- ✅ `/api/v1/favorites` endpoint now returns 1 favorite verse with proper timestamps
- ✅ No more Internal Server Error responses

### Prevention
Future entries will automatically get proper timestamps thanks to existing SQLAlchemy model configuration with `server_default=func.now()`.