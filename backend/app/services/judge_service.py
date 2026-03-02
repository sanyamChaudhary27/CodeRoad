import logging
import subprocess
import tempfile
import os
import json
import time
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Submission, SubmissionStatus, Challenge, Match

logger = logging.getLogger(__name__)

class JudgeService:
    """Service for evaluating code submissions."""
    
    def __init__(self):
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "command": ["python"],
                "timeout_seconds": 5
            }
        }

    def evaluate_submission(self, db: Session, submission_id: str) -> None:
        """
        Evaluate a submission by running it against test cases.
        This alters the submission in the database directly.
        """
        logger.info(f"Evaluating submission {submission_id}")
        
        # 1. Fetch data
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.error(f"Submission {submission_id} not found.")
            return

        try:
            # Update status
            submission.status = SubmissionStatus.EXECUTING
            db.commit()

            # Check language support
            lang_str = submission.language.value.lower() if hasattr(submission.language, 'value') else str(submission.language).lower()
            lang_config = self.supported_languages.get(lang_str)
            if not lang_config:
                submission.status = SubmissionStatus.COMPILE_ERROR
                submission.error_message = f"Unsupported language: {submission.language}"
                submission.completed_at = datetime.utcnow()
                db.commit()
                return

            # Fetch match then challenge — avoid lazy-load across thread boundary
            match = db.query(Match).filter(Match.id == submission.match_id).first()
            if not match:
                submission.status = SubmissionStatus.RUNTIME_ERROR
                submission.error_message = "Match not found for this submission"
                submission.completed_at = datetime.utcnow()
                db.commit()
                return

            challenge = db.query(Challenge).filter(Challenge.id == match.challenge_id).first()
            
            test_cases = []
            if challenge:
                try:
                    if challenge.test_cases:
                        test_cases.extend(json.loads(challenge.test_cases))
                except Exception as e:
                    logger.error(f"Failed to parse test cases: {e}")
            
            if not test_cases:
                logger.warning(f"No test cases found for challenge {match.challenge_id}")
                submission.status = SubmissionStatus.SUCCESS
                submission.test_cases_passed = 0
                submission.test_cases_total = 0
                submission.completed_at = datetime.utcnow()
                db.commit()
                return

            submission.test_cases_total = len(test_cases)
            
            # 2. Write code + driver to temp file
            # The driver reads stdin and calls solve() with the correct number
            # of arguments by inspecting the signature.
            PYTHON_DRIVER = '''

import sys as _sys
import inspect as _inspect

def _main():
    raw_input = _sys.stdin.read().strip()
    if not raw_input:
        return
        
    # Attempt to parse as integers
    try:
        input_data = list(map(int, raw_input.split()))
    except ValueError:
        # Fallback to list of strings
        input_data = raw_input.split()
        if len(input_data) == 1:
            input_data = input_data[0] # just the string
            
    if "solve" not in globals():
        print("Error: solve function not found")
        return
        
    solve_func = globals()["solve"]
    sig = _inspect.signature(solve_func)
    params = list(sig.parameters.values())
    
    # Heuristic for mapping input to function signature
    if len(params) == len(input_data):
        # e.g. solve(a, b) with "5 3" -> solve(5, 3)
        result = solve_func(*input_data)
    elif len(params) == 1:
        # e.g. solve(arr) with "5 7 2" -> solve([5, 7, 2])
        # Force list if it's multiple values
        result = solve_func(input_data)
    elif len(params) == 2:
        # e.g. solve(arr, x) with "2 7 11 15 9" -> solve([2, 7, 11, 15], 9)
        if isinstance(input_data, list) and len(input_data) >= 2:
            result = solve_func(input_data[:-1], input_data[-1])
        else:
            result = solve_func(input_data, None)
    else:
        # Fallback for 3+ args or other mismatches
        if isinstance(input_data, list):
            result = solve_func(*input_data[:len(params)])
        else:
            result = solve_func(input_data)

    # Consistent output formatting
    if result is None:
        print("")
    elif isinstance(result, (list, tuple)):
        print(" ".join(str(v) for v in result))
    elif isinstance(result, bool):
        print(str(result).lower())
    else:
        print(result)

_main()
'''
            passed = 0
            execution_times = []
            
            with tempfile.NamedTemporaryFile(suffix=lang_config["extension"], delete=False, mode='w', encoding='utf-8') as f:
                f.write(submission.code)
                f.write(PYTHON_DRIVER)
                temp_file_path = f.name

            try:
                # 3. Run against each test case
                for tc in test_cases:
                    input_data = tc.get("input", "")
                    expected_output = str(tc.get("expected_output", "")).strip()
                    
                    start_time = time.time()
                    
                    try:
                        process = subprocess.run(
                            lang_config["command"] + [temp_file_path],
                            input=input_data,
                            text=True,
                            capture_output=True,
                            timeout=lang_config["timeout_seconds"]
                        )
                        end_time = time.time()
                        
                        if process.returncode == 0:
                            actual_output = process.stdout.strip()
                            if actual_output == expected_output:
                                passed += 1
                            else:
                                logger.debug(f"TC failed: expected={repr(expected_output)}, got={repr(actual_output)}")
                            execution_times.append((end_time - start_time) * 1000)
                        else:
                            submission.error_message = process.stderr.strip()[:500]
                            
                    except subprocess.TimeoutExpired:
                        submission.status = SubmissionStatus.TIMEOUT
                        submission.error_message = "Execution timed out"
                        break
                    except Exception as e:
                        submission.status = SubmissionStatus.RUNTIME_ERROR
                        submission.error_message = str(e)[:500]
                        break

                # 4. Finalize Results
                submission.test_cases_passed = passed
                
                if execution_times:
                    submission.execution_time_ms = int(sum(execution_times) / len(execution_times))
                
                if submission.status == SubmissionStatus.EXECUTING:
                    if passed == len(test_cases):
                        submission.status = SubmissionStatus.SUCCESS
                    else:
                        submission.status = SubmissionStatus.RUNTIME_ERROR
                        
                submission.completed_at = datetime.utcnow()
                db.commit()
                
            finally:
                # Clean up
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
            logger.info(f"Submission {submission_id} evaluated: {passed}/{len(test_cases)} passed.")

        except Exception as e:
            # Catch-all: ensure status is always updated so the frontend never hangs
            logger.error(f"Unexpected error evaluating submission {submission_id}: {e}", exc_info=True)
            try:
                submission.status = SubmissionStatus.RUNTIME_ERROR
                submission.error_message = f"Internal judge error: {str(e)[:300]}"
                submission.completed_at = datetime.utcnow()
                db.commit()
            except Exception:
                pass
