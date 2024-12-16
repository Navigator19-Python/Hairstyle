import streamlit as st
from model import (
    initialize_db,
    register_user,
    login_user,
    fetch_hairstylists,
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

# View Hairstylists
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
                st.write("---")
        else:
            st.warning("No hairstylists found.")

# Book a Stylist
def book_stylist():
    st.subheader("📅 Book a Hairstylist")
    client_id = st.session_state.user["id"]
    stylist_id = st.number_input("Stylist ID", min_value=1, step=1)
    date = st.date_input("Booking Date")
    time = st.time_input("Booking Time")
    service_type = st.text_input("Service Type")
    price = st.number_input("Price", min_value=0.0, step=0.01)
    if st.button("Book Now"):
        add_booking(client_id, stylist_id, str(date), str(time), service_type, price)
        st.success("Booking request submitted successfully!")

# Hairstylist Profile Setup
def manage_hairstylist_profile(user_id):
    st.title("👩‍🎨 Hairstylist Profile Setup")
    st.markdown("Welcome to your hairstylist profile setup! 🌟")

    # Profile Details
    location = st.text_input("🗺️ Enter your location (e.g., Downtown, New York)")
    styles = st.multiselect(
        "✂️ Select the hairstyles you are capable of making:",
        ["Braiding", "Haircut", "Hair Coloring", "Weaving", "Dreadlocks", "Extensions", "Relaxing", "Curling"]
    )
    salon_price = st.number_input("💰 Price for Salon Service ($)", min_value=0.0, step=1.0, format="%.2f")
    home_price = st.number_input("💰 Price for Home Service ($)", min_value=0.0, step=1.0, format="%.2f")
    availability = st.text_area("🕒 Provide your availability (e.g., Mon-Fri, 10am-6pm)")
    style_images = st.file_uploader("📸 Upload images of your work (Optional)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    # Save Profile
    if st.button("💾 Save Profile"):
        if not location or not styles or not availability:
            st.error("Please complete all required fields to save your profile.")
        else:
            styles_str = ", ".join(styles)
            add_or_edit_hairstylist(user_id, "Your Name", styles_str, salon_price, home_price, availability, location, None)
            st.success("Your profile has been updated successfully! 🎉")
            st.markdown(f"""
            ### Your Profile Preview:
            - **Location**: {location}  
            - **Hairstyles**: {styles_str}  
            - **Salon Price**: ${salon_price}  
            - **Home Service Price**: ${home_price}  
            - **Availability**: {availability}  
            """)
            if style_images:
                st.markdown("**Uploaded Images:**")
                for img in style_images:
                    st.image(img, use_column_width=True)

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
    elif menu_choice == "Manage Profile" and st.session_state.user["user_type"] == "hairstylist":
        manage_hairstylist_profile(st.session_state.user["id"])
    elif menu_choice == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully!")
