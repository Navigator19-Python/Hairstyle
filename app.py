import streamlit as st
from model import (
    initialize_db,
    register_user,
    login_user,
    fetch_hairstylists,
    add_booking,
    add_review,
    update_pricing,
    save_hairstylist_profile,  # Assuming save_profile is defined
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
        st.experimental_set_query_params()  # Clears the query parameters (optional)
        st.info("Please log in again.")
        st.stop()  # Stops further execution

# Hairstylist Dashboard
def hairstylist_dashboard():
    st.sidebar.title("Hairstylist Menu")
    
    # Add a navigation sidebar for the hairstylist
    menu_choice = st.sidebar.radio(
        "Options",
        ["Manage Profile", "View Bookings", "Browse Hairstylists", "Logout"]
    )

    # If it's the first time the hairstylist is logging in
    if "has_profile" not in st.session_state.user:
        st.session_state.user["has_profile"] = False

    if not st.session_state.user["has_profile"]:
        st.subheader("👤 Complete Your Profile")
        name = st.text_input("Full Name", key="name")
        location = st.text_input("Location", key="location")
        availability = st.selectbox("Availability", ["Salon", "Home Visit", "Both"], key="availability")
        
        # Upload hairstyle pictures and set their prices for both services
        hairstyle_pictures = []
        prices = {"salon_price": 0.0, "home_price": 0.0}
        num_pictures = st.number_input("Number of Hairstyles to Upload", min_value=1, max_value=10, key="num_pictures")

        for i in range(num_pictures):
            picture = st.file_uploader(f"Upload Hairstyle {i+1}", type=["jpg", "png"], key=f"hairstyle_{i}")
            if picture:
                hairstyle_pictures.append(picture)
            salon_price = st.number_input(f"Salon Price for Hairstyle {i+1}", value=0.0, key=f"salon_price_{i}")
            home_price = st.number_input(f"Home Visit Price for Hairstyle {i+1}", value=0.0, key=f"home_price_{i}")
            prices["salon_price"] = salon_price
            prices["home_price"] = home_price

        if st.button("Save Profile"):
            if name and location and availability and hairstyle_pictures:
                # Save the profile info to the database (assuming a function save_profile exists)
                result = save_profile(
                    user_id=st.session_state.user["id"],
                    name=name,
                    location=location.strip().lower(),  # Normalize the location
                    availability=availability,
                    hairstyle_pictures=hairstyle_pictures,
                    prices=prices
                )
                if result["success"]:
                    st.session_state.user["has_profile"] = True
                    st.success("Profile updated successfully!")
                else:
                    st.error(result["message"])
            else:
                st.error("Please fill in all required fields and upload at least one hairstyle image.")

    # Navigation logic for when the profile is already created
    elif menu_choice == "Manage Profile":
        update_pricing()  # Allow hairstylist to update prices if profile is complete
    elif menu_choice == "View Bookings":
        # Here, you would display the hairstylist's bookings (this could be another function)
        view_bookings()
    elif menu_choice == "Browse Hairstylists":
        view_hairstylists()
    elif menu_choice == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully!")
        st.experimental_set_query_params()  # Clears the query parameters (optional)
        st.info("Please log in again.")
        st.stop()  # Stops further execution

# Function to view hairstylists (with location search fix)
def view_hairstylists():
    st.subheader("🔍 View Hairstylists")
    location = st.text_input("Search by Location", key="view_location").strip().lower()  # Normalize input
    if st.button("Search", key="search_stylists"):
        with st.spinner("Loading hairstylists..."):
            stylists = fetch_hairstylists(location)
            if stylists:
                for stylist in stylists:
                    # Normalize saved location for comparison (convert to lower case for case-insensitive matching)
                    if location in stylist['location'].strip().lower():  
                        st.markdown(f"""
                        - **Name**: {stylist['name']}
                        - **Location**: {stylist['location']}
                        - **Rating**: {stylist['rating']} ⭐
                        """)
            else:
                st.warning("No hairstylists found.")

# Function to update pricing (for hairstylists)
def update_pricing():
    st.subheader("💰 Update Pricing")
    salon_price = st.number_input("Salon Price", value=0.0)
    home_price = st.number_input("Home Visit Price", value=0.0)
    if st.button("Update Pricing"):
        result = update_pricing(
            stylist_id=st.session_state.user["id"], 
            salon_price=salon_price, 
            home_price=home_price
        )
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])

# Function to save hairstylist profile data (you need to implement this in the backend)
def save_profile(user_id, name, location, availability, hairstyle_pictures, prices):
    try:
        # Normalize location before saving
        location = location.strip().lower()
        # Save data to the database (your implementation here)
        return {"success": True, "message": "Profile saved successfully."}
    except Exception as e:
        return {"success": False, "message": f"Error saving profile: {e}"}

# Function to view bookings (dummy implementation, to be extended as per your needs)
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
else:
    if st.session_state.user["user_type"] == "client":
        client_dashboard()
    elif st.session_state.user["user_type"] == "hairstylist":
        hairstylist_dashboard()
    else:
        st.error("Unknown user type. Please contact support.")
