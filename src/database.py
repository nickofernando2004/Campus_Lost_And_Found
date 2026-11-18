"""
Database Management Module for the Campus Lost & Found System.

This module manages SQLite database connections and initializes the
relational schema required for user authentication, lost/found item
cataloging, and student ownership claim verification.
"""

import sqlite3
import os

# Define the relative path for the SQLite database file
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "campus_lost_found.db"
)


def get_connection():
    """
    Establish and return a connection to the SQLite database.

    Configures sqlite3.Row as the row factory so query results can be
    accessed by column name like a dictionary, and enables foreign key
    constraint enforcement.

    Returns:
        sqlite3.Connection: Active database connection object.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce relational integrity across foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Initialize all required database tables if they do not already exist.

    Creates three relational tables:
        1. users: Stores registered students and campus security/OSA admins.
        2. found_items: Logs items reported or turned in across campus.
        3. claims: Tracks student ownership claims and admin verification statuses.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table: Stores login credentials and role-based access levels
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Found Items Table: Stores reported items and their custody status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            location_found TEXT NOT NULL,
            date_found TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'unclaimed',
            reported_by INTEGER NOT NULL,
            FOREIGN KEY (reported_by) REFERENCES users(user_id)
        );
    """)

    # 3. Claims Table: Tracks student ownership claims awaiting admin review
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            claimant_id INTEGER NOT NULL,
            proof_description TEXT NOT NULL,
            claim_status TEXT NOT NULL DEFAULT 'pending',
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT,
            FOREIGN KEY (item_id) REFERENCES found_items(item_id),
            FOREIGN KEY (claimant_id) REFERENCES users(user_id)
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Run standalone test to verify schema creation
    init_db()
    print(f"Database initialized successfully at: {DB_PATH}")
