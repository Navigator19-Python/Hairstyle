from model import register_user, login_user, fetch_hairstylists, add_booking, add_or_edit_hairstylist 

# User Signup
def signup(username, password, user_type):
    result = register_user(username, password, user_type)
    if result["success"]:
        print(result["message"])
    else:
        print(f"Error: {result['message']}")

# User Login
def login(username, password):
    user = login_user(username, password)
    if user:
        print(f"Welcome, {user['username']}! You are logged in as a {user['user_type']}.")
        return user
    else:
        print("Invalid username or password.")
        return None

# Fetch all hairstylists
def view_hairstylists(location=None):
    stylists = fetch_hairstylists(location)
    if stylists:
        for stylist in stylists:
            print(f"Name: {stylist['name']}, Location: {stylist['location']}, Rating: {stylist['rating']}")
    else:
        print("No hairstylists found.")

# Book a stylist
def book_stylist(client_id, stylist_id, date, time, service_type, price):
    add_booking(client_id, stylist_id, date, time, service_type, price)
    print("Booking request submitted successfully.")

# Add or Edit Hairstylist Profile
def manage_hairstylist_profile(user_id, name, styles, salon_price, home_price, availability, location, image_bytes):
    add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, image_bytes)
    print("Hairstylist profile updated successfully.")

# Example Usage
if __name__ == "__main__":
    # Example: User signup
    signup("stylist_jane", "securepassword123", "hairstylist")

    # Example: User login
    user = login("stylist_jane", "securepassword123")
    
    if user:
        # Example: Add hairstylist profile
        if user["user_type"] == "hairstylist":
            manage_hairstylist_profile(
                user_id=user["id"],
                name="Jane Doe",
                styles="Braids, Cuts, Coloring",
                salon_price=50.0,
                home_price=70.0,
                availability="Mon-Fri, 10am-6pm",
                location="Downtown",
                image_bytes=None  # Replace with actual image bytes if needed
            )

        # Example: View hairstylists
        view_hairstylists(location="Downtown")

        # Example: Book a hairstylist
        book_stylist(client_id=2, stylist_id=1, date="2023-12-20", time="2:00 PM", service_type="Haircut", price=50.0)
