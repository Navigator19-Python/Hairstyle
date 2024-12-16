### Updated app.py
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
try:
    initialize_db()
    st.write("Database initialized successfully!")
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# Streamlit App Layout
st.title("\u2728 Hairstylist Booking App \u2702\ufe0f")

# State Management
if "user" not in st.session_state:
    st.session_state.user = None

# User Signup
def signup():
    st.subheader("\ud83d\udc64 Sign Up")
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
    st.subheader("🔑 Login")  # Replace with "Login" if Unicode still causes issues
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['username']}! You are logged in as a {user['user_type']}.")
        else:
            st.error("Invalid username or password.")

# Hairstylist Dashboard
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

# Client Dashboard
def client_dashboard():
    st.sidebar.title("Client Menu")
    menu_choice = st.sidebar.radio(
        "Options",
        ["View Hairstylists", "Logout"]
    )

    if menu_choice == "View Hairstylists":
        view_hairstylists()
    elif menu_choice == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully!")

# Hairstylist: Manage Profile
def manage_hairstylist_profile(user_id):
    st.title("\ud83d\udc69\u200d\ud83c\udfa8 Manage Hairstylist Profile")

    profile = fetch_hairstylist_profile(user_id)

    name = st.text_input("\ud83d\udcdb Hairstylist Name", value=profile["name"] if profile else "")
    location = st.text_input("\ud83d\udddf\ufe0f Location", value=profile["location"] if profile else "")
    styles = st.text_area("\u2702\ufe0f Hairstyles Offered", value=profile["styles"] if profile else "")
    salon_price = st.number_input("\ud83d\udcb0 Price for Salon Service ($)", min_value=0.0, value=profile["salon_price"] if profile else 0.0, step=1.0, format="%.2f")
    home_price = st.number_input("\ud83d\udcb0 Price for Home Service ($)", min_value=0.0, value=profile["home_price"] if profile else 0.0, step=1.0, format="%.2f")
    availability = st.text_area("\ud83d\udd52 Availability", value=profile["availability"] if profile else "")

    if st.button("\ud83d\udd13 Save Profile"):
        if not name or not location or not styles or not availability:
            st.error("Please complete all required fields to save your profile.")
        else:
            add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, None)
            st.success("Profile updated successfully!")

# Client: View Hairstylists
def view_hairstylists():
    st.subheader("\ud83d\udd0d View Hairstylists")
    location = st.text_input("Search by Location", key="view_location")
    if st.button("Search", key="search_stylists"):
        stylists = fetch_hairstylists(location)
        if stylists:
            for stylist in stylists:
                st.markdown(f"""
                - **Name**: {stylist['name']}
                - **Location**: {stylist['location']}
                - **Rating**: {stylist['rating']} \u2b50
                """)
                st.write("---")
        else:
            st.warning("No hairstylists found.")

# App Flow
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
    elif st.session_state.user["user_type"] == "client":
        client_dashboard()
