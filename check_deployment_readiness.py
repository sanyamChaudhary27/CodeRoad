#!/usr/bin/env python3
"""
Pre-deployment checklist script.
Verifies everything is ready before deploying to AWS.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_check(passed, message):
    icon = "✅" if passed else "❌"
    print(f"{icon} {message}")
    return passed

def check_gemini_api():
    """Check if Gemini API key is configured and working."""
    print_header("Checking Gemini API")
    
    env_file = Path("backend/.env")
    if not env_file.exists():
        print_check(False, "backend/.env file not found")
        return False
    
    with open(env_file) as f:
        content = f.read()
        if "GEMINI_API_KEY" not in content:
            print_check(False, "GEMINI_API_KEY not found in .env")
            return False
        
        # Extract API key
        for line in content.split('\n'):
            if line.startswith('GEMINI_API_KEY'):
                api_key = line.split('=')[1].strip()
                if api_key and len(api_key) > 20:
                    print_check(True, f"API key found: {api_key[:20]}...{api_key[-4:]}")
                    return True
    
    print_check(False, "Invalid API key format")
    return False

def check_frontend_build():
    """Check if frontend can build."""
    print_header("Checking Frontend Build")
    
    package_json = Path("frontend/package.json")
    if not package_json.exists():
        print_check(False, "frontend/package.json not found")
        return False
    
    print_check(True, "package.json exists")
    
    # Check if node_modules exists
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print_check(False, "node_modules not found - run 'npm install'")
        return False
    
    print_check(True, "node_modules exists")
    
    # Check if dist exists (previous build)
    dist = Path("frontend/dist")
    if dist.exists():
        print_check(True, "Previous build found in dist/")
    else:
        print_check(False, "No build found - run 'npm run build'")
        return False
    
    return True

def check_backend_dependencies():
    """Check if backend dependencies are installed."""
    print_header("Checking Backend Dependencies")
    
    requirements = Path("backend/requirements.txt")
    if not requirements.exists():
        print_check(False, "requirements.txt not found")
        return False
    
    print_check(True, "requirements.txt exists")
    
    # Try importing key packages
    try:
        import fastapi
        print_check(True, f"FastAPI installed (v{fastapi.__version__})")
    except ImportError:
        print_check(False, "FastAPI not installed")
        return False
    
    try:
        import sqlalchemy
        print_check(True, f"SQLAlchemy installed (v{sqlalchemy.__version__})")
    except ImportError:
        print_check(False, "SQLAlchemy not installed")
        return False
    
    try:
        import google.generativeai
        print_check(True, "google-generativeai installed")
    except ImportError:
        print_check(False, "google-generativeai not installed")
        return False
    
    return True

def check_database_config():
    """Check database configuration."""
    print_header("Checking Database Configuration")
    
    env_file = Path("backend/.env")
    if not env_file.exists():
        print_check(False, ".env file not found")
        return False
    
    with open(env_file) as f:
        content = f.read()
        
        if "DATABASE_URL" not in content:
            print_check(False, "DATABASE_URL not found in .env")
            return False
        
        # Check if using SQLite
        if "sqlite" in content.lower():
            print_check(False, "⚠️  WARNING: Using SQLite (not recommended for production)")
            print("   SQLite doesn't support concurrent connections properly")
            print("   WebSockets may fail with multiple users")
            print("   Recommendation: Use PostgreSQL instead")
            print("   See DEPLOYMENT_CONCERNS_ANSWERED.md for details")
            return False
        
        # Check if using PostgreSQL
        if "postgresql" in content.lower():
            print_check(True, "Using PostgreSQL (recommended)")
            return True
        
        print_check(False, "Unknown database type")
        return False

def check_cors_config():
    """Check CORS configuration."""
    print_header("Checking CORS Configuration")
    
    config_file = Path("backend/app/config.py")
    if not config_file.exists():
        print_check(False, "config.py not found")
        return False
    
    with open(config_file) as f:
        content = f.read()
        
        if "CORS_ORIGINS" not in content:
            print_check(False, "CORS_ORIGINS not found")
            return False
        
        print_check(True, "CORS_ORIGINS configured")
        
        # Check if has production URLs
        if "s3" in content.lower() or "cloudfront" in content.lower():
            print_check(True, "Production URLs configured")
        else:
            print_check(False, "⚠️  No production URLs in CORS (add after deployment)")
    
    return True

def check_git_status():
    """Check git status."""
    print_header("Checking Git Status")
    
    try:
        # Check if git repo
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "nothing to commit" in result.stdout:
            print_check(True, "All changes committed")
        else:
            print_check(False, "⚠️  Uncommitted changes found")
            print("   Consider committing before deployment")
        
        # Check current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        print_check(True, f"Current branch: {branch}")
        
        return True
        
    except subprocess.CalledProcessError:
        print_check(False, "Not a git repository or git not installed")
        return False

def check_aws_cli():
    """Check if AWS CLI is installed and configured."""
    print_header("Checking AWS CLI")
    
    try:
        result = subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print_check(True, f"AWS CLI installed: {result.stdout.strip()}")
        
        # Check if configured
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_check(True, "AWS credentials configured")
            return True
        else:
            print_check(False, "AWS credentials not configured - run 'aws configure'")
            return False
            
    except FileNotFoundError:
        print_check(False, "AWS CLI not installed")
        print("   Install from: https://aws.amazon.com/cli/")
        return False

def main():
    print("\n" + "🚀" * 30)
    print("  Code Road - Deployment Readiness Check")
    print("🚀" * 30)
    
    checks = {
        "Gemini API": check_gemini_api(),
        "Frontend Build": check_frontend_build(),
        "Backend Dependencies": check_backend_dependencies(),
        "Database Config": check_database_config(),
        "CORS Config": check_cors_config(),
        "Git Status": check_git_status(),
        "AWS CLI": check_aws_cli(),
    }
    
    print_header("Summary")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for name, result in checks.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "=" * 60)
    print(f"  {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✅ All checks passed! Ready for deployment!")
        print("\nNext steps:")
        print("1. Run: python test_gemini_api.py")
        print("2. Follow: QUICK_DEPLOY_GUIDE.md")
        print("3. Deploy by March 6, 2026")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Run 'npm install' in frontend/")
        print("- Run 'npm run build' in frontend/")
        print("- Run 'pip install -r requirements.txt' in backend/")
        print("- Update DATABASE_URL to use PostgreSQL")
        print("- Run 'aws configure' to setup AWS credentials")
        return 1

if __name__ == "__main__":
    sys.exit(main())
