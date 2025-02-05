import streamlit as st

# Simulated user database
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""

# Login function
def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USER_CREDENTIALS[username]["role"]
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()  # Refresh to show navigation
        else:
            st.error("Invalid username or password")

# Main app interface
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Admin Page", "User Page"])

    if page == "Home":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['username']}! You are logged in as {st.session_state['role']}.")

    elif page == "Admin Page" and st.session_state["role"] == "admin":
        st.title("Admin Dashboard")
        st.write("Welcome to the admin page.")

    elif page == "User Page" and st.session_state["role"] == "user":
        st.title("User Dashboard")
        st.write("Welcome to the user page.")

    else:
        st.error("Unauthorized access")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.experimental_rerun()

# Control access
if not st.session_state["logged_in"]:
    login()
else:
    main()
