import sqlite3
import bcrypt

# Database connection setup (thread-safe)
def get_db_connection():
    conn = sqlite3.connect('hairstylist_app.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database and create tables
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT, -- Password stored as bcrypt hash
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

    # Create Reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stylist_id INTEGER,
        client_id INTEGER,
        rating INTEGER,
        comment TEXT,
        FOREIGN KEY (stylist_id) REFERENCES hairstylists (id),
        FOREIGN KEY (client_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()

# User Registration
def register_user(username, password, user_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return {"success": False, "message": "Username already exists."}

        # Hash the password and insert user into database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                       (username, hashed_password, user_type))
        conn.commit()
        return {"success": True, "message": "User registered successfully."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}
    finally:
        conn.close()

# User Login
def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch user from database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            return None  # User not found

        # Convert Row object to dictionary for easier use
        user_dict = dict(user)

        # Verify password
        if 'password' in user_dict and user_dict['password']:
            stored_password = user_dict['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return user_dict
        return None  # Invalid password
    except Exception as e:
        print(f"Error during login: {e}")
        return None
    finally:
        conn.close()

# Add or Edit Hairstylist Profile
def add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, image_bytes):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert or update hairstylist profile
        cursor.execute('''
            INSERT OR REPLACE INTO hairstylists (user_id, name, styles, salon_price, home_price, availability, location, style_image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, name, styles, salon_price, home_price, availability, location, image_bytes))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error while adding/updating hairstylist profile: {e}")
    finally:
        conn.close()

# Fetch Hairstylists
def fetch_hairstylists(location=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch hairstylists based on location (if provided)
        query = 'SELECT * FROM hairstylists'
        params = []
        if location:
            query += " WHERE location LIKE ?"
            params.append(f"%{location}%")
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]  # Convert rows to dictionaries
    finally:
        conn.close()

# Add Booking
def add_booking(client_id, stylist_id, date, time, service_type, price):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Add booking to database
        cursor.execute('''
            INSERT INTO bookings (client_id, stylist_id, date, time, service_type, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (client_id, stylist_id, date, time, service_type, price, 'pending'))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error while adding booking: {e}")
    finally:
        conn.close()
