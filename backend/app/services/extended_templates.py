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
