"""Extended problem templates for different ELO levels"""

EXTENDED_TEMPLATES = [
    # BEGINNER (ELO 800-1100) - 6 problems
    {
        'title': 'Count Even Numbers',
        'description': 'Count how many even numbers are in the given array.',
        'difficulty': 'beginner',
        'domain': 'arrays',
        'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '0 ≤ x ≤ 1000'},
        'input_format': 'Array of integers',
        'output_format': 'Count of even numbers',
        'example_input': '1 2 3 4 5 6',
        'example_output': '3',
        'time_limit_seconds': 1,
        'test_cases': [
            {'id': 'tc1', 'input': '1 2 3 4 5 6', 'expected_output': '3', 'category': 'basic', 'description': 'Mixed numbers', 'is_hidden': False},
            {'id': 'tc2', 'input': '2 4 6 8', 'expected_output': '4', 'category': 'basic', 'description': 'All even', 'is_hidden': False},
            {'id': 'tc3', 'input': '1 3 5 7', 'expected_output': '0', 'category': 'edge', 'description': 'All odd', 'is_hidden': True},
            {'id': 'tc4', 'input': '0', 'expected_output': '1', 'category': 'edge', 'description': 'Zero is even', 'is_hidden': True}
        ]
    },
    {
        'title': 'Check Sorted Array',
        'description': 'Check if an array is sorted in ascending order.',
        'difficulty': 'beginner',
        'domain': 'arrays',
        'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'},
        'input_format': 'Array of integers',
        'output_format': 'true or false',
        'example_input': '1 2 3 4 5',
        'example_output': 'true',
        'time_limit_seconds': 1,
        'test_cases': [
            {'id': 'tc1', 'input': '1 2 3 4 5', 'expected_output': 'true', 'category': 'basic', 'description': 'Sorted array', 'is_hidden': False},
            {'id': 'tc2', 'input': '5 4 3 2 1', 'expected_output': 'false', 'category': 'basic', 'description': 'Reverse sorted', 'is_hidden': False},
            {'id': 'tc3', 'input': '1 1 1 1', 'expected_output': 'true', 'category': 'edge', 'description': 'All same', 'is_hidden': True},
            {'id': 'tc4', 'input': '1', 'expected_output': 'true', 'category': 'edge', 'description': 'Single element', 'is_hidden': True}
        ]
    },
    {
        'title': 'Find First Duplicate',
        'description': 'Find the first number that appears twice in the array. Return -1 if no duplicates.',
        'difficulty': 'beginner',
        'domain': 'arrays',
        'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '1 ≤ x ≤ 100'},
        'input_format': 'Array of integers',
        'output_format': 'First duplicate or -1',
        'example_input': '1 2 3 2 4',
        'example_output': '2',
        'time_limit_seconds': 1,
        'test_cases': [
            {'id': 'tc1', 'input': '1 2 3 2 4', 'expected_output': '2', 'category': 'basic', 'description': 'Has duplicate', 'is_hidden': False},
            {'id': 'tc2', 'input': '1 2 3 4 5', 'expected_output': '-1', 'category': 'basic', 'description': 'No duplicates', 'is_hidden': False},
            {'id': 'tc3', 'input': '5 5 5', 'expected_output': '5', 'category': 'edge', 'description': 'All same', 'is_hidden': True},
            {'id': 'tc4', 'input': '1', 'expected_output': '-1', 'category': 'edge', 'description': 'Single element', 'is_hidden': True}
        ]
    },
    
    # INTERMEDIATE (ELO 1100-1400) - 6 problems
    {
        'title': 'Valid Parentheses',
        'description': 'Check if a string of parentheses is valid. Valid means every opening bracket has a corresponding closing bracket in correct order.',
        'difficulty': 'intermediate',
        'domain': 'strings',
        'constraints': {'input_size': '1 ≤ n ≤ 1000', 'characters': '()[]{}'},
        'input_format': 'String of brackets',
        'output_format': 'true or false',
        'example_input': '()[]{}',
        'example_output': 'true',
        'time_limit_seconds': 2,
        'test_cases': [
            {'id': 'tc1', 'input': '()[]{}', 'expected_output': 'true', 'category': 'basic', 'description': 'Valid brackets', 'is_hidden': False},
            {'id': 'tc2', 'input': '([)]', 'expected_output': 'false', 'category': 'basic', 'description': 'Invalid order', 'is_hidden': False},
            {'id': 'tc3', 'input': '{[()]}', 'expected_output': 'true', 'category': 'edge', 'description': 'Nested valid', 'is_hidden': True},
            {'id': 'tc4', 'input': '((', 'expected_output': 'false', 'category': 'edge', 'description': 'Unclosed', 'is_hidden': True}
        ]
    },
    {
        'title': 'Rotate Array',
        'description': 'Rotate an array to the right by k steps.',
        'difficulty': 'intermediate',
        'domain': 'arrays',
        'constraints': {'input_size': '1 ≤ n ≤ 1000', 'value_range': '-1000 ≤ x ≤ 1000', 'k': '0 ≤ k ≤ n'},
        'input_format': 'Array and k (rotation steps)',
        'output_format': 'Rotated array',
        'example_input': '1 2 3 4 5 2',
        'example_output': '4 5 1 2 3',
        'time_limit_seconds': 2,
        'test_cases': [
            {'id': 'tc1', 'input': '1 2 3 4 5 2', 'expected_output': '4 5 1 2 3', 'category': 'basic', 'description': 'Basic rotation', 'is_hidden': False},
            {'id': 'tc2', 'input': '1 2 0', 'expected_output': '1 2', 'category': 'edge', 'description': 'No rotation', 'is_hidden': False},
            {'id': 'tc3', 'input': '1 2 3 3', 'expected_output': '1 2 3', 'category': 'edge', 'description': 'Full rotation', 'is_hidden': True},
            {'id': 'tc4', 'input': '1 1', 'expected_output': '1', 'category': 'edge', 'description': 'Single element', 'is_hidden': True}
        ]
    },
    {
        'title': 'Find Missing Number',
        'description': 'Given an array containing n distinct numbers from 0 to n, find the one missing number.',
        'difficulty': 'intermediate',
        'domain': 'arrays',
        'constraints': {'input_size': '1 ≤ n ≤ 10000', 'value_range': '0 ≤ x ≤ n'},
        'input_format': 'Array of n numbers',
        'output_format': 'Missing number',
        'example_input': '3 0 1',
        'example_output': '2',
        'time_limit_seconds': 2,
        'test_cases': [
            {'id': 'tc1', 'input': '3 0 1', 'expected_output': '2', 'category': 'basic', 'description': 'Missing middle', 'is_hidden': False},
            {'id': 'tc2', 'input': '0 1', 'expected_output': '2', 'category': 'basic', 'description': 'Missing last', 'is_hidden': False},
            {'id': 'tc3', 'input': '1', 'expected_output': '0', 'category': 'edge', 'description': 'Missing first', 'is_hidden': True},
            {'id': 'tc4', 'input': '9 6 4 2 3 5 7 0 1', 'expected_output': '8', 'category': 'boundary', 'description': 'Large array', 'is_hidden': True}
        ]
    },
    
    # ADVANCED (ELO 1400+) - 6 problems
    {
        'title': 'Trapping Rain Water',
        'description': 'Given n non-negative integers representing elevation map where width of each bar is 1, compute how much water it can trap after raining.',
        'difficulty': 'advanced',
        'domain': 'arrays',
        'constraints': {'input_size': '1 ≤ n ≤ 10000', 'value_range': '0 ≤ height ≤ 10000'},
        'input_format': 'Array of heights',
        'output_format': 'Total water trapped',
        'example_input': '0 1 0 2 1 0 1 3 2 1 2 1',
        'example_output': '6',
        'time_limit_seconds': 3,
        'test_cases': [
            {'id': 'tc1', 'input': '0 1 0 2 1 0 1 3 2 1 2 1', 'expected_output': '6', 'category': 'basic', 'description': 'Complex terrain', 'is_hidden': False},
            {'id': 'tc2', 'input': '4 2 0 3 2 5', 'expected_output': '9', 'category': 'basic', 'description': 'Multiple valleys', 'is_hidden': False},
            {'id': 'tc3', 'input': '1 2 3 4 5', 'expected_output': '0', 'category': 'edge', 'description': 'Ascending', 'is_hidden': True},
            {'id': 'tc4', 'input': '5 4 3 2 1', 'expected_output': '0', 'category': 'edge', 'description': 'Descending', 'is_hidden': True}
        ]
    },
    {
        'title': 'Minimum Window Substring',
        'description': 'Find the minimum window substring of s which contains all characters of string t.',
        'difficulty': 'advanced',
        'domain': 'strings',
        'constraints': {'input_size': '1 ≤ |s|, |t| ≤ 10000', 'character_set': 'ASCII'},
        'input_format': 'Two strings s and t',
        'output_format': 'Minimum window or empty string',
        'example_input': 'ADOBECODEBANC ABC',
        'example_output': 'BANC',
        'time_limit_seconds': 3,
        'test_cases': [
            {'id': 'tc1', 'input': 'ADOBECODEBANC ABC', 'expected_output': 'BANC', 'category': 'basic', 'description': 'Basic case', 'is_hidden': False},
            {'id': 'tc2', 'input': 'a a', 'expected_output': 'a', 'category': 'edge', 'description': 'Single char', 'is_hidden': False},
            {'id': 'tc3', 'input': 'a aa', 'expected_output': '', 'category': 'edge', 'description': 'Impossible', 'is_hidden': True},
            {'id': 'tc4', 'input': 'ab b', 'expected_output': 'b', 'category': 'boundary', 'description': 'Exact match', 'is_hidden': True}
        ]
    },
    {
        'title': 'Word Ladder',
        'description': 'Transform beginWord to endWord by changing one letter at a time. Each transformed word must exist in the word list. Return the length of shortest transformation sequence.',
        'difficulty': 'advanced',
        'domain': 'graphs',
        'constraints': {'input_size': '1 ≤ wordList.length ≤ 1000', 'word_length': '1 ≤ length ≤ 10'},
        'input_format': 'beginWord endWord wordList',
        'output_format': 'Shortest path length or 0',
        'example_input': 'hit cog hot dot dog lot log cog',
        'example_output': '5',
        'time_limit_seconds': 3,
        'test_cases': [
            {'id': 'tc1', 'input': 'hit cog hot dot dog lot log cog', 'expected_output': '5', 'category': 'basic', 'description': 'Path exists', 'is_hidden': False},
            {'id': 'tc2', 'input': 'hit cog hot dot dog lot log', 'expected_output': '0', 'category': 'basic', 'description': 'No path', 'is_hidden': False},
            {'id': 'tc3', 'input': 'a c a b c', 'expected_output': '2', 'category': 'edge', 'description': 'Short path', 'is_hidden': True},
            {'id': 'tc4', 'input': 'hot dog hot dot dog', 'expected_output': '3', 'category': 'boundary', 'description': 'Multiple paths', 'is_hidden': True}
        ]
    },
]


# Debug Arena Templates
DEBUG_TEMPLATES = [
    # BEGINNER DEBUG CHALLENGES
    {
        'title': 'Fix the Sum Function',
        'description': '''This function should add two numbers together and return the sum.

However, the tests are failing. Find and fix the bug!

Example:
- Input: 5, 3
- Expected: 8''',
        'difficulty': 'beginner',
        'domain': 'debugging',
        'challenge_type': 'debug',
        'bug_count': 1,
        'bug_types': ['logic'],
        'broken_code': '''def solve(arr):
    """Fix the bug: should add, not subtract"""
    a, b = arr[0], arr[1]
    return a - b''',
        'correct_solution': '''def solve(arr):
    """Add two numbers"""
    a, b = arr[0], arr[1]
    return a + b''',
        'constraints': {'input_size': 'Two integers', 'value_range': '-1000 ≤ x ≤ 1000'},
        'input_format': 'Two integers a and b',
        'output_format': 'Sum of a and b',
        'example_input': '5 3',
        'example_output': '8',
        'time_limit_seconds': 300,
        'test_cases': [
            {'id': 'tc1', 'input': '5 3', 'expected_output': '8', 'category': 'basic', 'description': 'Positive numbers', 'is_hidden': False},
            {'id': 'tc2', 'input': '0 0', 'expected_output': '0', 'category': 'edge', 'description': 'Zero', 'is_hidden': False},
            {'id': 'tc3', 'input': '-5 3', 'expected_output': '-2', 'category': 'basic', 'description': 'Negative number', 'is_hidden': True},
            {'id': 'tc4', 'input': '100 200', 'expected_output': '300', 'category': 'basic', 'description': 'Large numbers', 'is_hidden': True}
        ]
    },
    {
        'title': 'Fix the Loop',
        'description': '''This function should return a list of numbers from 1 to n (inclusive).

Example: For n=5, it should return [1, 2, 3, 4, 5]

The function is not producing the correct output. Find and fix the bug!''',
        'difficulty': 'beginner',
        'domain': 'debugging',
        'challenge_type': 'debug',
        'bug_count': 1,
        'bug_types': ['logic'],
        'broken_code': '''def solve(arr):
    """Count from 1 to n - has off-by-one error"""
    n = arr[0]
    result = []
    for i in range(1, n):
        result.append(i)
    return result''',
        'correct_solution': '''def solve(arr):
    """Count from 1 to n"""
    n = arr[0]
    result = []
    for i in range(1, n+1):
        result.append(i)
    return result''',
        'constraints': {'input_size': '1 ≤ n ≤ 100'},
        'input_format': 'Integer n',
        'output_format': 'List of numbers from 1 to n',
        'example_input': '5',
        'example_output': '[1, 2, 3, 4, 5]',
        'time_limit_seconds': 300,
        'test_cases': [
            {'id': 'tc1', 'input': '5', 'expected_output': '[1, 2, 3, 4, 5]', 'category': 'basic', 'description': 'Count to 5', 'is_hidden': False},
            {'id': 'tc2', 'input': '1', 'expected_output': '[1]', 'category': 'edge', 'description': 'Single element', 'is_hidden': False},
            {'id': 'tc3', 'input': '10', 'expected_output': '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]', 'category': 'basic', 'description': 'Count to 10', 'is_hidden': True}
        ]
    },
    
    # INTERMEDIATE DEBUG CHALLENGES
    {
        'title': 'Fix the Binary Search',
        'description': '''This binary search function should find the index of a target value in a sorted array.

It should return the index if found, or -1 if not found.

Example:
- Array: [1, 2, 3, 4, 5], Target: 3 → Returns 2
- Array: [1, 2, 3, 4, 5], Target: 6 → Returns -1

The function has bugs that cause errors or incorrect results. Find and fix ALL the bugs!''',
        'difficulty': 'intermediate',
        'domain': 'debugging',
        'challenge_type': 'debug',
        'bug_count': 2,
        'bug_types': ['logic', 'algorithm'],
        'broken_code': '''def solve(arr):
    """Binary search with bugs - causes IndexError or infinite loop"""
    target = arr[-1]
    search_arr = arr[:-1]
    
    left, right = 0, len(search_arr)
    
    while left <= right:
        mid = (left + right) // 2
        
        if search_arr[mid] == target:
            return mid
        elif search_arr[mid] < target:
            left = mid
        else:
            right = mid - 1
    
    return -1''',
        'correct_solution': '''def solve(arr):
    """Binary search - fixed version"""
    target = arr[-1]
    search_arr = arr[:-1]
    
    left, right = 0, len(search_arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if search_arr[mid] == target:
            return mid
        elif search_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1''',
        'constraints': {'input_size': '1 ≤ n ≤ 1000', 'value_range': 'Sorted array'},
        'input_format': 'Sorted array and target value',
        'output_format': 'Index of target or -1',
        'example_input': '[1, 2, 3, 4, 5] 3',
        'example_output': '2',
        'time_limit_seconds': 300,
        'test_cases': [
            {'id': 'tc1', 'input': '1 2 3 4 5 3', 'expected_output': '2', 'category': 'basic', 'description': 'Find middle', 'is_hidden': False},
            {'id': 'tc2', 'input': '1 2 3 4 5 1', 'expected_output': '0', 'category': 'edge', 'description': 'Find first', 'is_hidden': False},
            {'id': 'tc3', 'input': '1 2 3 4 5 6', 'expected_output': '-1', 'category': 'edge', 'description': 'Not found', 'is_hidden': True},
            {'id': 'tc4', 'input': '1 2 3 4 5 5', 'expected_output': '4', 'category': 'edge', 'description': 'Find last', 'is_hidden': True}
        ]
    },
    {
        'title': 'Fix the Palindrome Checker',
        'description': '''This function should check if a string is a palindrome (reads the same forwards and backwards).

It should ignore spaces and be case-insensitive.

Examples:
- "racecar" → True
- "A man a plan a canal Panama" → True  
- "hello" → False

The function is crashing with an error. Find and fix ALL the bugs!''',
        'difficulty': 'intermediate',
        'domain': 'debugging',
        'challenge_type': 'debug',
        'bug_count': 2,
        'bug_types': ['logic', 'edge_case'],
        'broken_code': '''def solve(arr):
    """Check if string is palindrome - has IndexError bug"""
    s = ' '.join(map(str, arr))
    s = s.lower().replace(" ", "")
    left, right = 0, len(s)
    
    while left <= right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    
    return True''',
        'correct_solution': '''def solve(arr):
    """Check if string is palindrome - fixed"""
    s = ' '.join(map(str, arr))
    s = s.lower().replace(" ", "")
    left, right = 0, len(s) - 1
    
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    
    return True''',
        'constraints': {'input_size': '1 ≤ length ≤ 1000'},
        'input_format': 'String as space-separated characters',
        'output_format': 'True or False',
        'example_input': 'r a c e c a r',
        'example_output': 'True',
        'time_limit_seconds': 300,
        'test_cases': [
            {'id': 'tc1', 'input': 'r a c e c a r', 'expected_output': 'True', 'category': 'basic', 'description': 'Simple palindrome', 'is_hidden': False},
            {'id': 'tc2', 'input': 'h e l l o', 'expected_output': 'False', 'category': 'basic', 'description': 'Not palindrome', 'is_hidden': False},
            {'id': 'tc3', 'input': 'A m a n a p l a n a c a n a l P a n a m a', 'expected_output': 'True', 'category': 'advanced', 'description': 'With spaces', 'is_hidden': True},
            {'id': 'tc4', 'input': 'a', 'expected_output': 'True', 'category': 'edge', 'description': 'Single char', 'is_hidden': True}
        ]
    },
    
    # ADVANCED DEBUG CHALLENGES
    {
        'title': 'Fix the Merge Sort',
        'description': '''This merge sort implementation should sort an array in ascending order.

Example:
- Input: [64, 34, 25, 12, 22, 11, 90]
- Output: [11, 12, 22, 25, 34, 64, 90]

The function has bugs that cause errors or incorrect results. Find and fix ALL the bugs!''',
        'difficulty': 'advanced',
        'domain': 'debugging',
        'challenge_type': 'debug',
        'bug_count': 3,
        'bug_types': ['logic', 'algorithm', 'edge_case'],
        'broken_code': '''def solve(arr):
    """Merge sort with bugs in merge function"""
    def merge_sort_helper(arr):
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = merge_sort_helper(arr[:mid])
        right = merge_sort_helper(arr[mid:])
        
        return merge(left, right)
    
    def merge(left, right):
        result = []
        i = j = 0
        
        while i < len(left) or j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        return result
    
    return merge_sort_helper(arr)''',
        'correct_solution': '''def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Test
print(merge_sort([64, 34, 25, 12, 22, 11, 90]))''',
        'constraints': {'input_size': '1 ≤ n ≤ 1000', 'value_range': '-10000 ≤ x ≤ 10000'},
        'input_format': 'Array of integers',
        'output_format': 'Sorted array',
        'example_input': '[64, 34, 25, 12, 22, 11, 90]',
        'example_output': '[11, 12, 22, 25, 34, 64, 90]',
        'time_limit_seconds': 300,
        'test_cases': [
            {'id': 'tc1', 'input': '64 34 25 12 22 11 90', 'expected_output': '[11, 12, 22, 25, 34, 64, 90]', 'category': 'basic', 'description': 'Random array', 'is_hidden': False},
            {'id': 'tc2', 'input': '5 4 3 2 1', 'expected_output': '[1, 2, 3, 4, 5]', 'category': 'basic', 'description': 'Reverse sorted', 'is_hidden': False},
            {'id': 'tc3', 'input': '1', 'expected_output': '[1]', 'category': 'edge', 'description': 'Single element', 'is_hidden': True},
            {'id': 'tc4', 'input': '1 1 1 1', 'expected_output': '[1, 1, 1, 1]', 'category': 'edge', 'description': 'All same', 'is_hidden': True}
        ]
    }
]

