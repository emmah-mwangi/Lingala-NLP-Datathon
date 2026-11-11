"""
Authentication module for the Lingala Intent Classifier.

Provides local SQLite-based authentication with secure password hashing.
This is a prototype implementation for the datathon - not for production use.

Security notes:
- Uses bcrypt for password hashing
- Passwords are never stored in plaintext
- Session state is used for login persistence during app runtime
- No production-grade security features (email verification, rate limiting, etc.)
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Optional

import bcrypt

# Database path - outside of git-tracked directories
DB_PATH = Path(__file__).resolve().parent.parent / "private" / "users.db"


def init_db() -> None:
    """Initialize the users database if it doesn't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_user(username: str, email: str, password: str, full_name: str) -> tuple[bool, str]:
    """
    Create a new user account.
    
    Returns:
        (success, message) tuple
    """
    init_db()
    
    # Validate inputs
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not email or "@" not in email:
        return False, "Invalid email address"
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not full_name:
        return False, "Full name is required"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, full_name)
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, f"Error creating account: {str(e)}"


def authenticate_user(username: str, password: str) -> tuple[bool, Optional[dict], str]:
    """
    Authenticate a user.
    
    Returns:
        (success, user_data, message) tuple
        user_data is None if authentication fails
    """
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        return False, None, "Invalid username or password"
    
    if not verify_password(password, user["password_hash"]):
        return False, None, "Invalid username or password"
    
    return True, dict(user), "Authentication successful"


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user data by ID."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user data by username."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user data by email."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None
