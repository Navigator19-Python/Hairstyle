import sqlite3
import hashlib
from geopy.geocoders import Nominatim  # To convert location to latitude/longitude

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
        latitude REAL,
        longitude REAL,
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
        rating REAL,
        review TEXT,
        FOREIGN KEY (stylist_id) REFERENCES hairstylists (id),
        FOREIGN KEY (client_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()

# Password Hashing
def hash_password(password):
    salt = "random_salt_value"  # Replace with a securely generated random salt per user
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

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

# Helper function to geocode a location (convert location to latitude/longitude)
def geocode_location(location):
    geolocator = Nominatim(user_agent="hairstylist_app")
    location = geolocator.geocode(location)
    if location:
        return location.latitude, location.longitude
    return None, None

# Hairstylist Management
def save_hairstylist_profile(user_id, name, location, availability, salon_price, home_price, style_images):
    latitude, longitude = geocode_location(location)
    if latitude is None or longitude is None:
        return {"success": False, "message": "Invalid location, unable to geocode."}

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO hairstylists (user_id, name, location, latitude, longitude, availability, salon_price, home_price, style_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, location, latitude, longitude, availability, salon_price, home_price, style_images))
        conn.commit()
        return {"success": True, "message": "Profile saved successfully."}
    except Exception as e:
        return {"success": False, "message": f"Error saving profile: {e}"}
    finally:
        conn.close()

# Fetch Hairstylists with Location Search
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

def update_pricing(stylist_id, salon_price, home_price):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE hairstylists
        SET salon_price = ?, home_price = ?
        WHERE id = ?
        ''', (salon_price, home_price, stylist_id))
        conn.commit()
        return {"success": True, "message": "Pricing updated successfully."}
    finally:
        conn.close()

# Booking Management
def add_booking(client_id, stylist_id, date, time, service_type, price):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT * FROM bookings 
        WHERE stylist_id = ? AND date = ? AND time = ? AND status = 'confirmed'
        ''', (stylist_id, date, time))
        if cursor.fetchone():
            return {"success": False, "message": "The selected time is unavailable."}

        cursor.execute('''
        INSERT INTO bookings (client_id, stylist_id, date, time, service_type, price, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
        ''', (client_id, stylist_id, date, time, service_type, price))
        conn.commit()
        return {"success": True, "message": "Booking request sent successfully."}
    finally:
        conn.close()

# Reviews Management
def add_review(stylist_id, client_id, rating, review):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO reviews (stylist_id, client_id, rating, review)
        VALUES (?, ?, ?, ?)
        ''', (stylist_id, client_id, rating, review))
        conn.commit()
        return {"success": True, "message": "Review added successfully."}
    finally:
        conn.close()

# Geo-location
def find_nearby_hairstylists(client_location, radius_km=5):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM hairstylists')
    stylists = cursor.fetchall()

    nearby_stylists = []
    for stylist in stylists:
        stylist_location = (stylist["latitude"], stylist["longitude"])
        distance = geodesic(client_location, stylist_location).km
        if distance <= radius_km:
            stylist_dict = dict(stylist)
            stylist_dict["distance"] = distance
            nearby_stylists.append(stylist_dict)

    return sorted(nearby_stylists, key=lambda x: x["distance"])
