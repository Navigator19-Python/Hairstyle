# requirements.txt
streamlit>=1.21.0
numpy>=1.25.0
pandas>=2.0.0
bcrypt>=4.0.1

---

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

# app.py
import streamlit as st
from model import (
    initialize_db,
    register_user,
    login_user,
    fetch_hairstylists,
    fetch_hairstylist_profile,
    add_booking,
    add_or_edit_hairstylist,
)

# Initialize Database
initialize_db()

# Streamlit App Layout
st.title("✨ Hairstylist Booking App ✂️")

# State Management
if "user" not in st.session_state:
    st.session_state.user = None

# User Signup
def signup():
    st.subheader("👤 Sign Up")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    user_type = st.selectbox("User Type", ["hairstylist", "client"], key="signup_user_type")
    if st.button("Sign Up"):
        result = register_user(username, password, user_type)
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])

# User Login
def login():
    st.subheader("🔑 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['username']}! You are logged in as a {user['user_type']}.")
        else:
            st.error("Invalid username or password.")

# Dashboard Routing
def hairstylist_dashboard():
    st.sidebar.title("Hairstylist Menu")
    menu_choice = st.sidebar.radio(
        "Options",
        ["Manage Profile", "Logout"]
    )

    if menu_choice == "Manage Profile":
        manage_hairstylist_profile(st.session_state.user["id"])
    elif menu_choice == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully!")

# Manage Hairstylist Profile
def manage_hairstylist_profile(user_id):
    st.title("👩‍🎨 Manage Hairstylist Profile")
    profile = fetch_hairstylist_profile(user_id)

    name = st.text_input("📛 Hairstylist Name", value=profile["name"] if profile else "")
    location = st.text_input("📽️ Location", value=profile["location"] if profile else "")
    styles = st.text_area("✂️ Hairstyles Offered", value=profile["styles"] if profile else "")
    salon_price = st.number_input("💰 Salon Service Price", min_value=0.0, value=profile["salon_price"] if profile else 0.0, step=1.0, format="%.2f")
    availability = st.text_area("🕒 Availability", value=profile["availability"] if profile else "")

    if st.button("🖾 Save Profile"):
        if not name or not location or not styles or not availability:
            st.error("All fields are required to save your profile.")
        else:
            add_or_edit_hairstylist(user_id, name, styles, salon_price, 0, availability, location, None)
            st.success("Profile updated successfully!")

# Main App Flow
if st.session_state.user is None:
    st.sidebar.title("Authentication")
    auth_choice = st.sidebar.radio("Choose an Option", ["Login", "Sign Up"])
    if auth_choice == "Sign Up":
        signup()
    elif auth_choice == "Login":
        login()
else:
    if st.session_state.user["user_type"] == "hairstylist":
        hairstylist_dashboard()
