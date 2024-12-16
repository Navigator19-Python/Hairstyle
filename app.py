import streamlit as st
from model import *

# User Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_type = None

# Login and Registration
st.sidebar.header("Log In")
if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Log In")
    
    if login_btn:
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.user_type = user[3]
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid username or password!")
else:
    st.sidebar.success(f"Logged in as {st.session_state.user_type.capitalize()}")

# Hairstylist Profile Management
if st.session_state.logged_in and st.session_state.user_type == 'hairstylist':
    st.title("Hairstylist Dashboard")
    with st.form("profile_form"):
        name = st.text_input("Name")
        styles = st.text_area("Describe Your Styles")
        salon_price = st.number_input("Salon Price", min_value=0.0)
        home_price = st.number_input("Home Service Price", min_value=0.0)
        availability = st.text_area("Availability (e.g., Mon-Fri 9am-5pm)")
        location = st.text_input("Your Location")
        style_image = st.file_uploader("Upload a Style Image", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Save Profile")
        
        if submit and style_image:
            image_bytes = style_image.read()
            add_or_edit_hairstylist(st.session_state.user_id, name, styles, salon_price, home_price, availability, location, image_bytes)
            st.success("Profile saved successfully!")

# Client Browsing Hairstylists
if st.session_state.logged_in and st.session_state.user_type == 'client':
    st.title("Browse Hairstylists")
    location_filter = st.text_input("Filter by Location (optional)")
    hairstylists = fetch_hairstylists(location_filter)
    
    for stylist in hairstylists:
        st.subheader(stylist[2])  # Name
        st.write(f"Styles: {stylist[3]}")
        st.write(f"Salon Price: ${stylist[4]}, Home Price: ${stylist[5]}")
        st.write(f"Location: {stylist[7]}")
        st.image(stylist[8], use_container_width=True)
        if st.button(f"Book {stylist[2]}"):
            st.session_state.stylist_id = stylist[0]
            st.session_state.booking_in_progress = True
            break

# Handle Booking (Booking Form)
if st.session_state.get("booking_in_progress"):
    stylist_id = st.session_state.get("stylist_id")
    st.title(f"Booking with Stylist {stylist_id}")
    date = st.date_input("Select Booking Date")
    time = st.time_input("Select Time")
    service_type = st.selectbox("Choose Service Type", ["Salon", "Home"])
    price = fetch_hairstylists()[stylist_id][4] if service_type == "Salon" else fetch_hairstylists()[stylist_id][5]
    
    if st.button("Confirm Booking"):
        cursor.execute('''
            INSERT INTO bookings (client_id, stylist_id, date, time, service_type, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (st.session_state.user_id, stylist_id, date, time, service_type, price, "pending"))
        conn.commit()
        st.success("Booking confirmed!")
