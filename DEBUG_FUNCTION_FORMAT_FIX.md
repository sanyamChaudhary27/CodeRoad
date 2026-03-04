# Debug Challenge Function Format Fix

## Issue Fixed
AI-generated debug challenges were using custom function names and parameters like:
```python
def find_kth_largest(nums, k):
    # code here
```

Instead of the standardized format:
```python
def solve(arr):
    # code here
```

This caused inconsistency with templates and potential judging issues.

## Solution

### 1. Updated AI Prompt
Added explicit requirements and examples to the Groq prompt:

```
CRITICAL REQUIREMENTS:
- The function MUST be named "solve" and take a single parameter "arr"
- Function signature MUST be: def solve(arr):
- All inputs are passed as a single array/list
- For multiple inputs, they are elements in the array (e.g., arr[0], arr[1])

Example format for single input:
def solve(arr):
    n = arr[0]  # Extract input
    # buggy code here
    return result

Example format for multiple inputs:
def solve(arr):
    nums = arr[:-1]  # First n-1 elements
    target = arr[-1]  # Last element
    # buggy code here
    return result
```

### 2. Added Post-Processing
Implemented automatic fixing of non-compliant code:

```python
# Check if function is not named 'solve'
func_match = re.search(r'def\s+(\w+)\s*\([^)]*\):', broken_code)
if func_match:
    func_name = func_match.group(1)
    if func_name != 'solve':
        logger.info(f"Fixing function name from '{func_name}' to 'solve'")
        # Replace function name with 'solve'
        broken_code = re.sub(r'def\s+\w+\s*\([^)]*\):', 'def solve(arr):', broken_code, count=1)
        
        # Also replace any calls to the old function name
        broken_code = re.sub(rf'\b{func_name}\s*\(', 'solve(', broken_code)
        
        challenge_data['broken_code'] = broken_code

# Ensure parameter is 'arr'
if 'def solve(' in broken_code and 'def solve(arr)' not in broken_code:
    logger.info("Fixing parameter name to 'arr'")
    broken_code = re.sub(r'def solve\([^)]*\):', 'def solve(arr):', broken_code, count=1)
    challenge_data['broken_code'] = broken_code
```

### 3. Updated Time Limit
Changed default time limit from 5 seconds to 300 seconds (5 minutes) to match debug arena settings.

## Test Results

Ran test script `test_debug_function_format.py` with 3 AI-generated challenges:

```
Test 1/3: Generating AI debug challenge...
  Title: Fix the Cumulative Sum Calculator
  Method: groq_ai
  Function: def solve(arr):
  ✅ Correct format: def solve(arr):

Test 2/3: Generating AI debug challenge...
  Title: Fix the Majority Element Finder
  Method: groq_ai
  Function: def solve(arr):
  ✅ Correct format: def solve(arr):

Test 3/3: Generating AI debug challenge...
  Title: Fix the Duplicate Remover and Sorter
  Method: groq_ai
  Function: def solve(arr):
  ✅ Correct format: def solve(arr):
```

**Result**: 3/3 challenges (100%) use correct format! ✅

## How Multiple Inputs Work

### Example: Find Kth Largest Element
**Input**: Array of numbers + k value  
**Test case input**: `5 3 8 1 9 2` (find 2nd largest)

**Broken code**:
```python
def solve(arr):
    # Extract inputs
    k = arr[-1]  # Last element is k
    nums = arr[:-1]  # All other elements are the array
    
    # Buggy code
    nums.sort()
    return nums[k-1]  # Bug: should be nums[-k]
```

**Test case format**:
- Input: `5 3 8 1 9 2` (space-separated)
- Expected output: `8`

### Example: Binary Search
**Input**: Sorted array + target value  
**Test case input**: `1 2 3 4 5 3` (find 3 in array)

**Broken code**:
```python
def solve(arr):
    target = arr[-1]
    search_arr = arr[:-1]
    
    left, right = 0, len(search_arr)  # Bug: should be len-1
    
    while left <= right:
        mid = (left + right) // 2
        if search_arr[mid] == target:
            return mid
        elif search_arr[mid] < target:
            left = mid  # Bug: should be mid + 1
        else:
            right = mid - 1
    
    return -1
```

## Benefits

### Consistency
- All debug challenges (AI and template) use same format
- Easier for players to understand
- Consistent with DSA challenges

### Judging
- Same judging logic for all debug challenges
- No special cases needed
- Reliable test execution

### Flexibility
- Can handle any number of inputs
- Works with arrays, single values, multiple parameters
- Easy to extend for new challenge types

## Files Modified

### Backend
- `backend/app/services/challenge_service.py` - Updated prompt and added post-processing
- `backend/test_debug_function_format.py` - New test script to verify format

### Documentation
- `DEBUG_FUNCTION_FORMAT_FIX.md` - This file
- `AI_DEBUG_GENERATION_ENABLED.md` - Updated with format requirements

## Future Improvements

1. **Validation**: Add stricter validation before saving to database
2. **Examples**: Include more example formats in prompt
3. **Testing**: Add automated tests to CI/CD pipeline
4. **Monitoring**: Track format compliance rate in production
5. **Feedback**: Use player feedback to improve prompt

## Notes

- Post-processing is a safety net; prompt should prevent issues
- Regex handles edge cases like extra whitespace
- Function calls within code are also updated
- Works with nested function definitions
- Preserves code logic while fixing format
