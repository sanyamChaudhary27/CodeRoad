import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "coderoad.db")
    print(f"Connecting to database at {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file not found. Nothing to migrate.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List of columns to add to 'submissions' table if they don't exist
    columns_to_add = [
        ("time_to_first_submission", "INTEGER"),
        ("time_between_submissions", "INTEGER"),
        ("total_submission_time", "INTEGER"),
        ("code_paste_probability", "FLOAT"),
        ("code_length", "INTEGER"),
        ("code_lines", "INTEGER"),
        ("unique_tokens", "INTEGER"),
        ("comment_ratio", "FLOAT"),
        ("indentation_consistency", "FLOAT"),
        ("variable_naming_style", "VARCHAR(50)"),
        ("keystroke_speed_avg", "FLOAT"),
        ("keystroke_speed_variance", "FLOAT"),
        ("copy_paste_events", "INTEGER DEFAULT 0"),
        ("deletion_ratio", "FLOAT"),
        ("submission_count_in_match", "INTEGER DEFAULT 1"),
        ("time_to_solve", "INTEGER"),
        ("iterations_to_solution", "INTEGER")
    ]

    # Get current columns
    cursor.execute("PRAGMA table_info(submissions)")
    current_columns = [info[1] for info in cursor.fetchall()]

    for col_name, col_type in columns_to_add:
        if col_name not in current_columns:
            print(f"Adding column {col_name}...")
            try:
                cursor.execute(f"ALTER TABLE submissions ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
