import sqlite3
import hashlib

# Database Connection
def get_db_connection():
    conn = sqlite3.connect('hairstylist_app.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize Database
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        user_type TEXT -- 'hairstylist' or 'client'
    )
    ''')

    # Create Hairstylists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hairstylists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        styles TEXT,
        salon_price REAL,
        home_price REAL,
        availability TEXT,
        location TEXT,
        style_image BLOB,
        rating REAL DEFAULT 0.0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create Bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        stylist_id INTEGER,
        date TEXT,
        time TEXT,
        service_type TEXT,
        price REAL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (client_id) REFERENCES users (id),
        FOREIGN KEY (stylist_id) REFERENCES hairstylists (id)
    )
    ''')

    conn.commit()
    conn.close()

# Password Hashing
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# User Functions
def register_user(username, password, user_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return {"success": False, "message": "Username already exists."}

        hashed_password = hash_password(password)
        cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                       (username, hashed_password, user_type))
        conn.commit()
        return {"success": True, "message": "User registered successfully."}
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and hash_password(password) == user["password"]:
            return dict(user)
        return None
    finally:
        conn.close()

# Fetch Hairstylists
def fetch_hairstylists(location=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = 'SELECT * FROM hairstylists'
        params = []
        if location:
            query += ' WHERE location LIKE ?'
            params.append(f'%{location}%')
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
