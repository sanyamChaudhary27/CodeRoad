"""
Test script to verify debug challenges use correct function format
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.challenge_service import get_challenge_service
from app.core.database import get_db
import re

def test_function_format():
    """Test that AI-generated debug challenges use def solve(arr): format"""
    service = get_challenge_service()
    db = next(get_db())
    
    print("\n=== Testing Debug Challenge Function Format ===\n")
    
    try:
        # Generate 3 AI challenges
        for i in range(3):
            print(f"Test {i+1}/3: Generating AI debug challenge...")
            challenge = service.generate_debug_challenge(
                db=db,
                difficulty='intermediate',
                player_rating=300,
                use_ai=True,
                player_id=None
            )
            
            print(f"  Title: {challenge['title']}")
            print(f"  Method: {challenge.get('generation_method', 'unknown')}")
            
            # Check function signature
            broken_code = challenge.get('broken_code', '')
            
            # Extract function definition
            func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\):', broken_code)
            
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2).strip()
                
                print(f"  Function: def {func_name}({params}):")
                
                # Verify format
                if func_name == 'solve' and params == 'arr':
                    print(f"  ✅ Correct format: def solve(arr):")
                else:
                    print(f"  ❌ WRONG format! Expected: def solve(arr):")
                    print(f"     Got: def {func_name}({params}):")
                    print(f"\n  Broken code preview:")
                    print("  " + "\n  ".join(broken_code.split('\n')[:5]))
            else:
                print(f"  ❌ No function definition found!")
                print(f"  Broken code: {broken_code[:200]}")
            
            print()
        
        print("=== Test Complete ===")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_function_format()
