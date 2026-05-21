from app.core.database import SessionLocal
from app.models.player import Player
from app.core.security import get_password_hash

def update_test_user():
    db = SessionLocal()
    try:
        user = db.query(Player).filter(Player.username == "testuser").first()
        if user:
            print(f"Updating password for {user.username}...")
            user.hashed_password = get_password_hash("password123")
            db.commit()
            print("Successfully updated password!")
        else:
            print("User 'testuser' not found. Creating new...")
            user = Player(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                current_rating=1200.0
            )
            db.add(user)
            db.commit()
            print("Successfully created testuser!")
    finally:
        db.close()

if __name__ == "__main__":
    update_test_user()
