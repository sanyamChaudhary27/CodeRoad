"""
Migration script to add profile_picture column to players table
"""
import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'coderoad.db')

def add_profile_picture_column():
    """Add profile_picture column to players table"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_picture' in columns:
            print("✓ Column 'profile_picture' already exists in players table")
            conn.close()
            return
        
        # Add the column
        cursor.execute("""
            ALTER TABLE players 
            ADD COLUMN profile_picture VARCHAR(500)
        """)
        
        conn.commit()
        print("✓ Successfully added 'profile_picture' column to players table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_picture' in columns:
            print("✓ Verification successful - column exists")
        else:
            print("✗ Verification failed - column not found")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Adding profile_picture column to players table...")
    add_profile_picture_column()
    print("\nMigration complete!")
