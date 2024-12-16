import streamlit as st
from model import (
    initialize_db,
    register_user,
    login_user,
    fetch_hairstylists,
    fetch_hairstylist_profile,
    add_booking,
    fetch_booking_requests,
    update_booking_status,
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
                if st.button(f"View Full Profile (ID: {stylist['id']})", key=f"profile_{stylist['id']}"):
                    show_full_profile(stylist["id"])
                st.write("---")
        else:
            st.warning("No hairstylists found.")

# Client: View Full Profile of Hairstylist with Booking Option
def show_full_profile(hairstylist_id):
    st.subheader("📋 Hairstylist Full Profile")
    profile = fetch_hairstylist_profile(hairstylist_id)
    if profile:
        st.markdown(f"""
        - **Name**: {profile['name']}
        - **Location**: {profile['location']}
        - **Styles Offered**: {profile['styles']}
        - **Salon Price**: ${profile['salon_price']}
        - **Home Service Price**: ${profile['home_price']}
        - **Availability**: {profile['availability']}
        """)
        st.write("---")
        st.subheader("📅 Book This Hairstylist")
        client_id = st.session_state.user["id"]
        date = st.date_input("Booking Date")
        time = st.time_input("Booking Time")
        service_type = st.text_input("Service Type")
        price = st.number_input("Price", min_value=0.0, step=0.01)

        if st.button("Book Now"):
            add_booking(client_id, hairstylist_id, str(date), str(time), service_type, price)
            st.success("Booking request submitted successfully!")
    else:
        st.error("Profile not found.")

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
