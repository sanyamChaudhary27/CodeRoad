import sys
import os

# Add the current directory to sys.path to resolve 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.player import Player
from app.core.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        username = "testuser"
        email = "test@example.com"
        password = "password123"
        
        # Check if user already exists
        user = db.query(Player).filter(
            (Player.username == username) | (Player.email == email)
        ).first()
        
        if user:
            print(f"User with username '{username}' or email '{email}' already exists.")
            print(f"Using existing credentials:")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password: password123 (assuming it matches)")
            return

        test_user = Player(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            current_rating=300,
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print(f"Test user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
