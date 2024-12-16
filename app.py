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
