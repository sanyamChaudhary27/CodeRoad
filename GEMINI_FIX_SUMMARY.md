# Gemini Problem Generation - Complete Diagnosis & Fixes

## Executive Summary

You were seeing repeated problems (Two Sum, Palindrome, Merge Sorted Arrays, etc.) because:
1. **Gemini API quota was exhausted** - Free tier limit reached
2. **Classification model was using wrong model name** - `gemini-1.5-flash` doesn't exist
3. **No error logging** - Failures were silent, making debugging difficult

## Issues Identified

### Issue 1: Gemini API Quota Exceeded (CRITICAL)
**Problem:** Free tier quota exhausted
```
Error: 429 You exceeded your current quota
Quota metrics exceeded:
  - generativelanguage.googleapis.com/generate_content_free_tier_requests
  - generativelanguage.googleapis.com/generate_content_free_tier_input_token_count
```

**Why it happens:**
- Free tier has daily/minute rate limits
- Multiple test calls consumed the quota
- API key is on free tier plan

**Impact:**
- Gemini cannot generate new problems
- Service falls back to templates
- Users see same problems repeatedly

**Solution:**
- Wait for quota reset (usually daily)
- Upgrade to paid plan (recommended)
- Use different API key with available quota

---

### Issue 2: Wrong Model Name in Classification (MEDIUM)
**Problem:** Using `gemini-1.5-flash` which doesn't exist
```
Error: 404 models/gemini-1.5-flash is not found
```

**File:** `backend/app/services/integrity_service.py` (line 37)

**Before:**
```python
self.model = genai.GenerativeModel("gemini-1.5-flash")
```

**After:**
```python
self.model = genai.GenerativeModel("gemini-2.0-flash")
```

**Impact:**
- Classification model fails silently
- All submissions show "Human" classification
- Integrity analysis doesn't work

**Status:** ✅ FIXED

---

### Issue 3: No Error Logging for API Failures (MEDIUM)
**Problem:** Errors were caught but not logged with details

**File:** `backend/app/services/challenge_service.py` (line 118)

**Before:**
```python
response = self.gemini_model.generate_content(prompt, request_options={"timeout": 15.0})
text = response.text.strip()
```

**After:**
```python
try:
    response = self.gemini_model.generate_content(prompt, request_options={"timeout": 15.0})
    text = response.text.strip()
except Exception as e:
    error_msg = str(e)
    if "429" in error_msg:
        logger.error(f"Gemini API quota exceeded: {error_msg[:100]}")
    elif "404" in error_msg:
        logger.error(f"Gemini model not found: {error_msg[:100]}")
    else:
        logger.error(f"Gemini API error: {error_msg[:100]}")
    raise
```

**Impact:**
- Better debugging when API fails
- Can distinguish between quota, model, and other errors
- Helps identify issues faster

**Status:** ✅ FIXED

---

## Test Results

### Gemini Generation Test
```
✓ GEMINI_API_KEY loaded correctly
✓ google-generativeai package installed
✓ Gemini API configured
✓ Model creation works
✗ Text generation fails (quota exceeded)
```

### Classification Model Test
```
✓ GEMINI_API_KEY loaded correctly
✓ google-generativeai package installed
✓ Gemini API configured
✗ Model creation fails (gemini-1.5-flash not found) - NOW FIXED
```

### Available Models
```
✓ 44 models available
✓ gemini-2.0-flash available
✓ gemini-2.5-flash available
✗ gemini-1.5-flash NOT available
```

---

## How to Resolve Quota Issue

### Option 1: Wait for Reset (Free)
- Free tier quota resets daily (usually UTC midnight)
- Check status: https://ai.google.dev/rate-limits
- Wait and try again tomorrow

### Option 2: Upgrade to Paid Plan (Recommended)
1. Go to Google Cloud Console
2. Enable billing for your project
3. Upgrade to paid tier
4. Set up billing alerts

### Option 3: Use Different API Key
1. Create new Google Cloud project
2. Generate new API key
3. Update `backend/.env` with new key

---

## Fixes Applied

### Fix 1: Update Model Name ✅
**File:** `backend/app/services/integrity_service.py`
- Changed `gemini-1.5-flash` → `gemini-2.0-flash`
- Classification model will now work when quota is available

### Fix 2: Add Error Logging ✅
**File:** `backend/app/services/challenge_service.py`
- Added try-catch with specific error logging
- Can now distinguish between quota, model, and other errors
- Better debugging for future issues

### Fix 3: Config Loading ✅ (from previous fix)
**File:** `backend/app/config.py`
- Fixed to load from `backend/.env` explicitly
- GEMINI_API_KEY now loads correctly

---

## Testing Scripts Created

### 1. `test_gemini_generation.py`
Tests if Gemini can generate problem text
```bash
python test_gemini_generation.py
```

### 2. `test_classification_model.py`
Tests if classification model can predict AI vs Human
```bash
python test_classification_model.py
```

### 3. `test_gemini_models.py`
Lists available models and checks quota status
```bash
python test_gemini_models.py
```

---

## What Happens Now

### When Quota is Available:
1. User requests challenge
2. ChallengeService tries Gemini API
3. Gemini generates unique problem
4. Problem is returned to user
5. ✅ User sees new, unique problems

### When Quota is Exhausted:
1. User requests challenge
2. ChallengeService tries Gemini API
3. API returns 429 (quota exceeded)
4. Error is logged: "Gemini API quota exceeded"
5. Falls back to templates
6. User sees template-based problem
7. ⚠️ User sees repeated problems

### Classification Model:
1. Submission received
2. IntegrityService analyzes code
3. Uses `gemini-2.0-flash` (now correct)
4. Returns AI probability (0-100)
5. ✅ Shows correct classification (Human/AI)

---

## Recommendations

### Short-term:
1. Wait for quota reset or upgrade plan
2. Monitor logs for "Gemini API quota exceeded" errors
3. Test classification model when quota is available

### Medium-term:
1. Implement request caching to reduce API calls
2. Add rate limiting to prevent quota exhaustion
3. Set up monitoring/alerts for quota usage

### Long-term:
1. Migrate to `google.genai` package (current one is deprecated)
2. Implement batch API for bulk generation
3. Consider alternative AI providers as backup

---

## Files Modified

1. `backend/app/config.py` - Fixed .env loading
2. `backend/app/services/integrity_service.py` - Fixed model name
3. `backend/app/services/challenge_service.py` - Added error logging

## Files Created

1. `test_gemini_generation.py` - Test problem generation
2. `test_classification_model.py` - Test classification
3. `test_gemini_models.py` - Check available models
4. `GEMINI_ISSUES_DIAGNOSIS.md` - Detailed diagnosis
5. `GEMINI_FIX_SUMMARY.md` - This file

---

## Next Steps

1. **Check quota status:**
   ```bash
   python test_gemini_models.py
   ```

2. **If quota available, test generation:**
   ```bash
   python test_gemini_generation.py
   ```

3. **If quota available, test classification:**
   ```bash
   python test_classification_model.py
   ```

4. **If quota exhausted:**
   - Wait for reset, or
   - Upgrade to paid plan, or
   - Use different API key

5. **Monitor logs:**
   - Look for "Gemini API quota exceeded" errors
   - Look for "Gemini model not found" errors
   - Look for other "Gemini API error" messages
