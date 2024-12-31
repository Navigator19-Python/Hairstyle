import streamlit as st
from hairstyle_model import (
    initialize_db,
    register_user,
    login_user,
    fetch_hairstylists,
)

# Initialize Database
try:
    initialize_db()
except Exception as e:
    st.error("Error initializing the database. Check logs for more details.")
    st.stop()

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

# Client: View Hairstylists
def view_hairstylists():
    st.subheader("🔍 View Hairstylists")
    location = st.text_input("Search by Location", key="view_location")
    if st.button("Search", key="search_stylists"):
        stylists = fetch_hairstylists(location)
        if stylists:
            for stylist in stylists:
                st.markdown(f"""
                - **Name**: {stylist['name']}
                - **Location**: {stylist['location']}
                - **Rating**: {stylist['rating']} ⭐
                """)
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
    if st.session_state.user["user_type"] == "client":
        client_dashboard()
    else:
        st.error("You do not have access to this section.")
