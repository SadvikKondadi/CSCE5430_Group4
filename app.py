import streamlit as st
from pymongo import MongoClient

# Simulated user database
client = MongoClient('mongodb+srv://krrish852456:krrish852456@cluster0.99khz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')


db = client["slms"]
collection = db["slms"]


# Session state initialization
if "reg_in" not in st.session_state:
    st.session_state["reg_in"] = False
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""

#Reg function
def reg(x):
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    N=st.text_input("Name")
    'Already have an Account'
    if st.button('Login Page'):
        st.session_state["reg_in"] = False
        st.experimental_rerun()
        
    if st.button("Register"):
        if collection.find_one({"id": new_username}) is not None:
            st.warning("The UserID already EXIST.")
        else:
            if new_username and new_password:
                y={"id":new_username,"name":N,"pwd":new_password,"role":x}
                ind=collection.insert_one(y)
                st.session_state["reg_in"] = False
                st.experimental_rerun()
            else:
                st.warning("Please enter both username and password.")

# Login function
def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    'Create an Account'
    if st.button('Registration form'):
        st.session_state["reg_in"] = True
        st.experimental_rerun()
    if st.button("Login"):
            user = collection.find_one({"id": username})
            if user["pwd"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.experimental_rerun()  # Refresh to show navigation
       
# Main app interface Student
def mains():
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

# Main app interface Admin
def maina():
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

# Main app interface Instructor
def maini():
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
if not st.session_state["reg_in"]:
    if not st.session_state["logged_in"]:
        login()
    else:
        if st.session_state['role']=='Student':
            mains()
        if st.session_state['role']=='Admin':
            maina()
        if st.session_state['role']=='Instructor':
            maini()

else:
    reg("Student")