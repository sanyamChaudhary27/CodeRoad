# Gemini Problem Generation Issues - Diagnosis Report

## Issues Found

### Issue 1: Gemini API Quota Exceeded ⚠️ CRITICAL
**Status:** The free tier quota for Gemini API has been exhausted.

**Evidence:**
- Error: `429 You exceeded your current quota`
- Quota metrics exceeded:
  - `generativelanguage.googleapis.com/generate_content_free_tier_requests`
  - `generativelanguage.googleapis.com/generate_content_free_tier_input_token_count`

**Why this happens:**
- Free tier has daily/minute rate limits
- Multiple test calls and development usage consumed the quota
- The API key is on a free tier plan

**Impact:**
- Gemini cannot generate new problems
- Service falls back to template-based challenges
- Users see the same problems repeatedly (Two Sum, Palindrome, Merge Sorted Arrays, etc.)

**Solutions:**
1. **Wait for quota reset** (usually daily at UTC midnight)
2. **Upgrade to paid plan** (recommended for production)
3. **Use a different API key** with available quota
4. **Implement rate limiting** in the application to avoid quota exhaustion

---

### Issue 2: Classification Model Using Wrong Model ⚠️ MEDIUM
**Status:** The integrity service is trying to use `gemini-1.5-flash` which is not available.

**Evidence:**
- Error: `404 models/gemini-1.5-flash is not found`
- Available models: `gemini-2.0-flash`, `gemini-2.5-flash`, etc.

**Why this happens:**
- `gemini-1.5-flash` was deprecated or never available on this API key
- The code hardcodes model names that may not be available

**Impact:**
- Classification model cannot run
- Submissions always show "Human" classification
- Integrity analysis fails silently

**Solutions:**
1. Update `integrity_service.py` to use `gemini-2.0-flash` instead
2. Add fallback model selection
3. Check available models at runtime

---

### Issue 3: Deprecated Package Warning ⚠️ LOW
**Status:** Using deprecated `google-generativeai` package

**Evidence:**
- Warning: "All support for the `google.generativeai` package has ended"
- Recommendation: Switch to `google.genai` package

**Impact:**
- Package may stop working in future
- No new features or bug fixes

**Solutions:**
- Migrate to `google.genai` package (future task)

---

## Root Cause Analysis

### Why You're Seeing Repeated Problems

```
User requests challenge
    ↓
ChallengeService.generate_challenge() called with use_ai=True
    ↓
Checks: use_ai=True and self.ai_available and self.gemini_model?
    ↓
Tries to call Gemini API
    ↓
API returns 429 (Quota Exceeded)
    ↓
Exception caught, falls back to templates
    ↓
Returns template-based challenge (same ones over and over)
```

### Why Classification Always Shows "Human"

```
Submission received
    ↓
IntegrityService.analyze_submission() called
    ↓
Tries to use gemini-1.5-flash model
    ↓
API returns 404 (Model not found)
    ↓
Exception caught, ai_prob = 0.0
    ↓
overall = (paste_prob * 0.4) + (0.0 * 0.6) = low probability
    ↓
Shows "Human" classification
```

---

## Immediate Fixes

### Fix 1: Update integrity_service.py to use available model

**File:** `backend/app/services/integrity_service.py`

**Change:**
```python
# Before:
self.model = genai.GenerativeModel("gemini-1.5-flash")

# After:
self.model = genai.GenerativeModel("gemini-2.0-flash")
```

### Fix 2: Add error handling and logging

**File:** `backend/app/services/challenge_service.py`

Add better error logging to distinguish between:
- Quota exceeded (429)
- Model not found (404)
- Other errors

### Fix 3: Implement rate limiting

Add request throttling to avoid quota exhaustion:
- Cache generated problems
- Reuse problems for similar difficulty/domain
- Implement exponential backoff on quota errors

---

## Quota Management Recommendations

### For Development:
1. Use template-based generation during development
2. Only enable AI generation when needed
3. Set `use_ai=False` by default in development

### For Production:
1. Upgrade to paid Gemini API plan
2. Set up billing alerts
3. Implement request caching
4. Monitor quota usage
5. Use batch API for bulk generation

### Quota Limits (Free Tier):
- Requests per minute: Limited
- Requests per day: Limited
- Input tokens per minute: Limited
- Output tokens per minute: Limited

---

## Testing Results

### Gemini Generation Test
- ✓ API key loaded correctly
- ✓ Gemini configured successfully
- ✓ Model creation works
- ✗ Text generation fails (quota exceeded)

### Classification Model Test
- ✓ API key loaded correctly
- ✓ Gemini configured successfully
- ✗ Model creation fails (model not found)
- ✗ Classification fails

### Available Models
- ✓ 44 models available
- ✓ `gemini-2.0-flash` available
- ✓ `gemini-2.5-flash` available
- ✗ `gemini-1.5-flash` NOT available

---

## Next Steps

1. **Immediate:** Fix the model name in `integrity_service.py`
2. **Short-term:** Wait for quota reset or upgrade API plan
3. **Medium-term:** Implement rate limiting and caching
4. **Long-term:** Migrate to `google.genai` package
