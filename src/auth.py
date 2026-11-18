"""
Authentication and User Management Module for the Campus Lost & Found System.

Provides secure user registration and login functionality using SHA-256
password hashing and role-based access control ('student' or 'admin').
"""

import hashlib
import sqlite3
from src.database import get_connection


def hash_password(password: str) -> str:
    """
    Generate a SHA-256 cryptographic hash for a plaintext password.

    Args:
        password (str): The raw plaintext password entered by the user.

    Returns:
        str: A 64-character hexadecimal SHA-256 digest.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str, role: str = "student") -> bool:
    """
    Register a new user account in the SQLite database.

    Validates non-empty credentials and restricts roles to 'student' or 'admin'.

    Args:
        username (str): Unique login identifier for the user.
        password (str): Plaintext password to be hashed before storage.
        role (str, optional): Account privilege level ('student' or 'admin').
            Defaults to 'student'.

    Returns:
        bool: True if registration succeeds, False otherwise.
    """
    username = username.strip()
    role = role.strip().lower()

    # Validate non-empty inputs
    if not username or not password:
        print("Error: Username and password cannot be empty.")
        return False

    # Enforce allowed role types
    if role not in ("student", "admin"):
        print("Error: Role must be either 'student' or 'admin'.")
        return False

    password_hash = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert new user record using parameterized query to prevent SQL injection
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
        print(f"Registration successful! Account '{username}' created with role '{role}'.")
        return True
    except sqlite3.IntegrityError:
        # Handle duplicate username constraint violation
        print(f"Error: Username '{username}' is already taken.")
        return False
    finally:
        conn.close()


def login_user(username: str, password: str) -> dict | None:
    """
    Authenticate an existing user against stored credentials.

    Args:
        username (str): The username attempting to log in.
        password (str): The plaintext password to verify.

    Returns:
        dict | None: A dictionary containing 'user_id', 'username', and 'role'
            if credentials match; None if authentication fails.
    """
    username = username.strip()
    password_hash = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    # Query user matching both username and hashed password
    cursor.execute(
        "SELECT user_id, username, role FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash),
    )
    user_row = cursor.fetchone()
    conn.close()

    if user_row:
        user_data = dict(user_row)
        print(f"Login successful! Welcome, {user_data['username']} ({user_data['role']}).")
        return user_data

    print("Error: Invalid username or password.")
    return None
