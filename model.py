# model.py
import sqlite3
import bcrypt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# User Functions
def register_user(username, password, user_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return {"success": False, "message": "Username already exists."}

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                       (username, hashed_password, user_type))
        conn.commit()
        return {"success": True, "message": "User registered successfully."}
    except Exception as e:
        logging.error(f"Error in register_user: {e}")
        return {"success": False, "message": "Registration failed."}
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            return dict(user)
        return None
    except Exception as e:
        logging.error(f"Error in login_user: {e}")
        return None
    finally:
        conn.close()

# Hairstylist Profile
def fetch_hairstylist_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM hairstylists WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logging.error(f"Error in fetch_hairstylist_profile: {e}")
        return None
    finally:
        conn.close()

def add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, image_bytes):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO hairstylists (user_id, name, styles, salon_price, home_price, availability, location, style_image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, name, styles, salon_price, home_price, availability, location, image_bytes))
        conn.commit()
    except Exception as e:
        logging.error(f"Error in add_or_edit_hairstylist: {e}")
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
    except Exception as e:
        logging.error(f"Error in fetch_hairstylists: {e}")
        return []
    finally:
        conn.close()

# Booking Functions
def add_booking(client_id, stylist_id, date, time, service_type, price):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO bookings (client_id, stylist_id, date, time, service_type, price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        ''', (client_id, stylist_id, date, time, service_type, price))
        conn.commit()
    except Exception as e:
        logging.error(f"Error in add_booking: {e}")
    finally:
        conn.close()

---
