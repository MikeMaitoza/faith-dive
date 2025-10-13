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

## Fix: Database Schema Defaults (2025-10-11 - Follow-up)

### Problem
- Even after fixing existing NULL timestamps, new journal entries were still getting NULL values for `created_at` and `updated_at`
- SQLAlchemy `server_default=func.now()` was not being properly translated to SQLite DEFAULT values
- Creating new entries resulted in 500 Internal Server Error due to timestamp validation

### Root Cause
The database schema didn't have proper DEFAULT constraints. SQLAlchemy's `server_default=func.now()` wasn't creating the actual DEFAULT values in the SQLite schema.

### Solution Applied
Recreated tables with proper SQLite DEFAULT constraints:

```sql
-- Journal entries table with proper defaults
CREATE TABLE journal_entries (
    -- ... other columns ...
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now'))
);

-- Favorite verses table with proper defaults  
CREATE TABLE favorite_verses (
    -- ... other columns ...
    created_at DATETIME DEFAULT (datetime('now'))
);
```

### Verification
- ✅ New journal entries now save successfully with proper timestamps
- ✅ New favorite verses save successfully with proper timestamps
- ✅ API endpoints return 200 OK instead of 500 errors
- ✅ All existing data preserved during schema migration

### Final Result
Both creating and reading journal entries and favorites now work perfectly with automatic timestamp generation.
