import streamlit as st
from model import (
    initialize_db,
    register_user,
    login_user,
    fetch_hairstylists,
    add_booking,
    add_review,
    update_pricing,
    save_hairstylist_profile,  # Corrected import
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
        if not username.isalnum():
            st.error("Username must be alphanumeric.")
            return
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
        st.experimental_rerun()  # Ensures the app returns to the login/signup page

# Hairstylist Dashboard
def hairstylist_dashboard():
    st.sidebar.title("Hairstylist Menu")
    menu_choice = st.sidebar.radio(
        "Options",
        ["Manage Profile", "View Bookings", "Browse Hairstylists", "Logout"]
    )

    if menu_choice == "Manage Profile":
        manage_profile()
    elif menu_choice == "View Bookings":
        view_bookings()
    elif menu_choice == "Browse Hairstylists":
        view_hairstylists()
    elif menu_choice == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully!")
        st.experimental_rerun()

# Manage Profile for Hairstylist
def manage_profile():
    st.subheader("👤 Manage Your Profile")
    name = st.text_input("Full Name")
    location = st.text_input("Location")
    availability = st.selectbox("Availability", ["Salon", "Home Visit", "Both"])
    salon_price = st.number_input("Salon Price", value=0.0)
    home_price = st.number_input("Home Visit Price", value=0.0)
    style_images = st.file_uploader("Upload Hairstyle Images", accept_multiple_files=True)

    if st.button("Save Profile"):
        if name and location and availability and style_images:
            result = save_hairstylist_profile(
                user_id=st.session_state.user["id"],
                name=name,
                location=location.strip().lower(),
                availability=availability,
                salon_price=salon_price,
                home_price=home_price,
                style_images=style_images
            )
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])
        else:
            st.error("Please fill in all required fields.")

# Function to view hairstylists
def view_hairstylists():
    st.subheader("🔍 View Hairstylists")
    location = st.text_input("Search by Location").strip().lower()
    if st.button("Search"):
        with st.spinner("Loading hairstylists..."):
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

# Function to view bookings
def view_bookings():
    st.subheader("Your Bookings")
    st.write("Here you can view your upcoming bookings.")

# App Flow
if st.session_state.user is None:
    st.sidebar.title("Authentication")
    auth_choice = st.sidebar.radio("Choose an Option", ["Login", "Sign Up"])
    if auth_choice == "Sign Up":
        signup()
    elif auth_choice == "Login":
        login()
    st.stop()
else:
    if st.session_state.user["user_type"] == "client":
        client_dashboard()
    elif st.session_state.user["user_type"] == "hairstylist":
        hairstylist_dashboard()
    else:
        st.error("Unknown user type. Please contact support.")
