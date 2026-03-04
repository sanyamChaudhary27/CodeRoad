# Prompt Clarity Fix - Array Input Specification

## Problem Identified

The AI was generating ambiguous problems where it wasn't clear if the input was:
- A single-element array: `[1]`
- Or a single number: `1`

### Example of Ambiguous Problem:
```
Input: "1"
Expected Output: "0"
```

Is this:
- Array `[1]` → find index of first occurrence → output `0` ✓
- Number `1` → do something → output `0` ❓

## Solution Applied

Updated the prompt to be CRYSTAL CLEAR about input format:

### Key Changes:

1. **Explicit Function Signature**:
   ```
   Function MUST be: def solve(arr): where arr is a list
   NEVER use: def solve(a, b): or def solve(n):
   ```

2. **Input Format Clarity**:
   ```
   Input is ALWAYS an array (even if it has one element)
   - Input "5" means the array [5], NOT the number 5
   - Input "1 2 3" means the array [1, 2, 3]
   ```

3. **Description Requirements**:
   ```
   MUST start with "Given an array of integers..."
   Clearly explain that input is always an array
   ```

4. **Updated Test Case Examples**:
   ```json
   {
     "input": "7",
     "expected_output": "0",
     "description": "Single-element array [7]"
   }
   ```
   
   Instead of:
   ```json
   {
     "input": "1",
     "expected_output": "1",
     "description": "Single element"  // Ambiguous!
   }
   ```

5. **Added Reminder**:
   ```
   REMEMBER: Input "7" means the array [7] (single element), NOT the number 7!
   ```

## Expected Behavior After Fix

### Before (Ambiguous):
```
Problem: Find Index of First Occurrence
Input: "1"
Description: "...the smallest element..."
```
→ Unclear if `1` is an array or number

### After (Clear):
```
Problem: Find Index of First Occurrence
Input: "7"
Description: "Given an array of integers, find the index..."
Test: "Single-element array [7]"
```
→ Crystal clear that input is always an array

## Testing

After restarting the server, new problems should:
1. Always use `def solve(arr):` signature
2. Always describe input as "an array of integers"
3. Test case descriptions clarify single-element arrays
4. No ambiguity about whether input is array or number

## Files Modified

- `backend/app/services/challenge_service.py` - Updated prompt with explicit array requirements

## Next Steps

1. Restart the server to load the new prompt
2. Request a new practice match
3. Verify the problem description is clear about arrays
4. Check that test cases explicitly mention "array"
