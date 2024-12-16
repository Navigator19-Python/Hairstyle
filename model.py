import sqlite3

# Initialize SQLite database
conn = sqlite3.connect('hairstylist_app.db')
cursor = conn.cursor()

# Create Users Table (for both hairstylists and clients)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    user_type TEXT -- 'hairstylist' or 'client'
)''')

# Create Hairstylists Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS hairstylists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    styles TEXT,
    salon_price REAL,
    home_price REAL,
    availability TEXT,
    location TEXT, -- e.g., city or area
    style_image BLOB,
    rating REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')

# Create Bookings Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    stylist_id INTEGER,
    date TEXT,
    time TEXT,
    service_type TEXT, -- 'salon' or 'home'
    price REAL,
    status TEXT, -- 'pending', 'confirmed', 'completed'
    FOREIGN KEY (client_id) REFERENCES users (id),
    FOREIGN KEY (stylist_id) REFERENCES hairstylists (id)
)''')

# Create Reviews Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stylist_id INTEGER,
    client_id INTEGER,
    rating INTEGER,
    comment TEXT,
    FOREIGN KEY (stylist_id) REFERENCES hairstylists (id),
    FOREIGN KEY (client_id) REFERENCES users (id)
)''')
conn.commit()

# User Authentication
def register_user(username, password, user_type):
    cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                   (username, password, user_type))
    conn.commit()

def login_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    return cursor.fetchone()

# Add/Edit Hairstylist Profile
def add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, image_bytes):
    cursor.execute('''
        INSERT OR REPLACE INTO hairstylists (user_id, name, styles, salon_price, home_price, availability, location, style_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, name, styles, salon_price, home_price, availability, location, image_bytes))
    conn.commit()

# Fetch Hairstylists for Client Browsing
def fetch_hairstylists(location=None):
    query = 'SELECT * FROM hairstylists'
    if location:
        query += f" WHERE location LIKE '%{location}%'"
    cursor.execute(query)
    return cursor.fetchall()
