# Server Restart Required

## Problem
Python has cached the old version of `challenge_service.py` in memory. Even though the file has been updated with the correct Groq code, the running server and Python processes are still using the old cached bytecode.

## Solution
You MUST restart the backend server to load the new code.

## Steps

1. **Stop the current server**:
   - Go to the terminal running `uvicorn`
   - Press `CTRL+C` to stop it

2. **Clear all Python cache** (run these commands):
   ```bash
   Remove-Item -Recurse -Force backend/app/__pycache__
   Remove-Item -Recurse -Force backend/app/services/__pycache__
   Remove-Item -Recurse -Force backend/app/models/__pycache__
   Remove-Item -Recurse -Force backend/app/core/__pycache__
   Remove-Item -Recurse -Force backend/app/api/__pycache__
   ```

3. **Restart the server**:
   ```bash
   cd backend
   uvicorn app.app:app --reload
   ```

4. **Verify it's working**:
   - Look for these log messages:
     - `INFO:app.services.challenge_service:Groq client 1 initialized`
     - `INFO:app.services.challenge_service:Groq client 2 initialized`
     - ... (up to 5)
     - `INFO:app.services.challenge_service:Groq AI initialized with 5 API keys`
   
   - You should NOT see:
     - Any warnings about `google.generativeai`
     - `FutureWarning` about Gemini

5. **Test AI generation**:
   - Request a practice match
   - Look for: `INFO:app.services.challenge_service:Attempting Groq AI generation`
   - Should see: `INFO:app.services.challenge_service:Using Groq key 1/5`

## What Was Fixed

The file `backend/app/services/challenge_service.py` now has:
- ✅ Groq AI only (no Gemini)
- ✅ 5 API keys with rotation
- ✅ ELO-smart difficulty (beginner < 500, intermediate 500-800, advanced 800+)
- ✅ Boilerplate code cleaning

## If It Still Doesn't Work

If you still see Gemini warnings or template generation after restarting:

1. Check the file directly:
   ```bash
   Get-Content backend/app/services/challenge_service.py | Select-Object -First 20
   ```
   - Line 14-16 should say `from groq import Groq`
   - Should NOT say `import google.generativeai`

2. Verify environment variables:
   ```bash
   Get-Content backend/.env | Select-String "GROQ"
   ```
   - Should show all 5 GROQ_API_KEY variables

3. If problem persists, there may be another file importing the old code. Check:
   ```bash
   Get-ChildItem -Recurse -Filter "*.py" | Select-String "google.generativeai"
   ```
