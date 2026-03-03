#!/usr/bin/env python
import shutil

# Copy the fixed version to the main file
shutil.copy('backend/app/services/challenge_service_fixed.py', 'backend/app/services/challenge_service.py')

# Verify
with open('backend/app/services/challenge_service.py', 'r') as f:
    content = f.read()
    if 'def get_challenge_service' in content:
        print(f"SUCCESS: Copied {len(content)} bytes, function found")
    else:
        print("FAILED: Function not found")
