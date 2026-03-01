import logging
import subprocess
import tempfile
import os
import json
import time
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Submission, SubmissionStatus, Challenge, TestCase

logger = logging.getLogger(__name__)

class JudgeService:
    """Service for evaluating code submissions."""
    
    def __init__(self):
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "command": ["python"],
                "timeout_seconds": 2
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

        # Update status
        submission.status = SubmissionStatus.EXECUTING
        db.commit()

        # Check language support
        lang_config = self.supported_languages.get(submission.language.value.lower() if hasattr(submission.language, 'value') else submission.language.lower())
        if not lang_config:
            submission.status = SubmissionStatus.COMPILE_ERROR
            submission.error_message = f"Unsupported language: {submission.language}"
            submission.completed_at = datetime.utcnow()
            db.commit()
            return

        # Fetch challenge and test cases
        challenge = db.query(Challenge).filter(Challenge.id == submission.match.challenge_id).first()
        
        test_cases = []
        try:
            if challenge.test_cases:
                test_cases.extend(json.loads(challenge.test_cases))
            if challenge.hidden_test_cases:
                test_cases.extend(json.loads(challenge.hidden_test_cases))
        except Exception as e:
            logger.error(f"Failed to parse test cases: {e}")
        
        if not test_cases:
            submission.status = SubmissionStatus.SUCCESS
            submission.test_cases_passed = 0
            submission.test_cases_total = 0
            submission.completed_at = datetime.utcnow()
            db.commit()
            return

        submission.test_cases_total = len(test_cases)
        
        # 2. Write code to temp file
        passed = 0
        execution_times = []
        
        with tempfile.NamedTemporaryFile(suffix=lang_config["extension"], delete=False, mode='w') as f:
            f.write(submission.code)
            temp_file_path = f.name

        try:
            # 3. Run against each test case
            for tc in test_cases:
                input_data = tc.get("input", "")
                expected_output = tc.get("expected_output", "").strip()
                
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
                # If it didn't break due to error/timeout
                if passed == len(test_cases):
                    submission.status = SubmissionStatus.SUCCESS
                else:
                    submission.status = SubmissionStatus.RUNTIME_ERROR # Or 'Failed'
                    
            submission.completed_at = datetime.utcnow()
            db.commit()
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
        logger.info(f"Submission {submission_id} evaluated: {passed}/{len(test_cases)} passed.")