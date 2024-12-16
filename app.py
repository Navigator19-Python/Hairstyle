import streamlit as st
from model import register_user, login_user, fetch_hairstylists, add_booking, add_or_edit_hairstylist

# Streamlit App Layout
st.title("Hairstylist Booking App")

# State Management
if "user" not in st.session_state:
    st.session_state.user = None

# User Signup
def signup():
    st.subheader("Sign Up")
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
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['username']}! You are logged in as a {user['user_type']}.")
        else:
            st.error("Invalid username or password.")

# View Hairstylists
def view_hairstylists():
    st.subheader("View Hairstylists")
    location = st.text_input("Search by Location", key="view_location")
    if st.button("Search", key="search_stylists"):
        stylists = fetch_hairstylists(location)
        if stylists:
            for stylist in stylists:
                st.write(f"**Name**: {stylist['name']}")
                st.write(f"**Location**: {stylist['location']}")
                st.write(f"**Rating**: {stylist['rating']}")
                st.write("---")
        else:
            st.warning("No hairstylists found.")

# Book a Stylist
def book_stylist():
    st.subheader("Book a Hairstylist")
    client_id = st.session_state.user["id"]
    stylist_id = st.number_input("Stylist ID", min_value=1, step=1)
    date = st.date_input("Booking Date")
    time = st.time_input("Booking Time")
    service_type = st.text_input("Service Type")
    price = st.number_input("Price", min_value=0.0, step=0.01)
    if st.button("Book Now"):
        add_booking(client_id, stylist_id, str(date), str(time), service_type, price)
        st.success("Booking request submitted successfully.")

# Add/Edit Hairstylist Profile
def manage_profile():
    st.subheader("Manage Hairstylist Profile")
    user_id = st.session_state.user["id"]
    name = st.text_input("Name")
    styles = st.text_area("Styles (comma-separated)")
    salon_price = st.number_input("Salon Price", min_value=0.0, step=0.01)
    home_price = st.number_input("Home Service Price", min_value=0.0, step=0.01)
    availability = st.text_area("Availability (e.g., Mon-Fri, 10am-6pm)")
    location = st.text_input("Location")
    if st.button("Save Profile"):
        add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, None)
        st.success("Profile updated successfully.")

# App Flow
if st.session_state.user is None:
    st.sidebar.title("Authentication")
    auth_choice = st.sidebar.radio("Choose an Option", ["Login", "Sign Up"])
    if auth_choice == "Sign Up":
        signup()
    elif auth_choice == "Login":
        login()
else:
    st.sidebar.title("Menu")
    menu_choice = st.sidebar.radio(
        "Navigation",
        ["View Hairstylists", "Book a Stylist", "Manage Profile", "Logout"]
    )
    if menu_choice == "View Hairstylists":
        view_hairstylists()
    elif menu_choice == "Book a Stylist":
        book_stylist()
    elif menu_choice == "Manage Profile":
        manage_profile()
    elif menu_choice == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully.")
