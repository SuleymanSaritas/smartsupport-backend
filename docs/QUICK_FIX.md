# Quick Fix for Recent Activity Issue (No Docker Rebuild Required)

## Problem
Recent activities are not showing up in the frontend, but you don't want to rebuild Docker (takes 30 minutes).

## Solution: Restart Containers (No Rebuild)

Since we have hot reload enabled, you can restart containers to pick up code changes:

```bash
# Stop containers
docker-compose down

# Start containers (no rebuild, uses existing images)
docker-compose up -d

# Or restart specific services
docker-compose restart backend worker
```

## Debug Steps

### 1. Check Database Status
Use the new debug endpoint to see what's in the database:

```bash
curl -X GET "http://localhost:8000/api/v1/debug/db" \
  -H "X-API-Key: your-api-key"
```

This will show:
- Database file path
- Total ticket count
- Sample tickets
- Database file size

### 2. Check History Endpoint
Test the history endpoint directly:

```bash
curl -X GET "http://localhost:8000/api/v1/history?limit=10" \
  -H "X-API-Key: your-api-key"
```

### 3. Check Worker Logs
See if tickets are being saved:

```bash
docker-compose logs worker | grep "SAVING TO DB"
docker-compose logs worker | grep "saved to DB successfully"
```

### 4. Check Database File
If running locally, check if the database file exists:

```bash
# On Windows (PowerShell)
ls smartsupport.db

# Check file size
(Get-Item smartsupport.db).Length
```

## Common Issues & Fixes

### Issue 1: Database file not found
**Symptom:** Debug endpoint shows `database_exists: false`

**Fix:** The database path might be wrong. Check the logs:
```bash
docker-compose logs backend | grep "Database connected"
```

### Issue 2: No tickets in database
**Symptom:** `total_tickets: 0` in debug endpoint

**Fix:** 
1. Check if worker is processing tasks:
   ```bash
   docker-compose logs worker
   ```
2. Submit a test ticket and watch logs:
   ```bash
   docker-compose logs -f worker
   ```

### Issue 3: Database locked
**Symptom:** Errors about database being locked

**Fix:** Restart both containers:
```bash
docker-compose restart backend worker
```

## Force Database Re-initialization

If the database seems corrupted, you can delete it and let it recreate:

```bash
# Stop containers
docker-compose down

# Delete database file (if exists locally)
rm smartsupport.db
# Or on Windows:
del smartsupport.db

# Start containers (database will be recreated)
docker-compose up -d
```

## Verify Everything Works

1. **Submit a test ticket:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/tickets" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"text": "I need help with my account"}'
   ```

2. **Wait for task to complete** (check status endpoint)

3. **Check history:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/history" \
     -H "X-API-Key: your-api-key"
   ```

4. **Check debug endpoint:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/debug/db" \
     -H "X-API-Key: your-api-key"
   ```

## Notes

- Hot reload is enabled, so code changes should be picked up automatically
- If you see "SAVING TO DB..." in worker logs but no data, check database file permissions
- The database file should be in the project root directory
- Both backend and worker share the same database file via volume mount

