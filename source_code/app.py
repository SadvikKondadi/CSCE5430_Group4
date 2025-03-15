import streamlit as st
from pymongo import MongoClient


# Simulated user database
client = MongoClient('mongodb+srv://krrish852456:krrish852456@cluster0.99khz.mongodb.net/?retryWrites=true&w=majority&appid=Cluster0')

db = client["slms"]
dba=client['assign']
collection = db["slms"]
collection1 = db["Subjects"]
collection2 = db["Instructor"]
cust = db["Customer Care"]
assign=db["assign"]
m=db["modules"]
p=db["payment"]
fs = gridfs.GridFS(db)
fsa = gridfs.GridFS(dba)
# Session state initialization
if "reg_in" not in st.session_state:
    st.session_state["reg_in"] = False
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""


#Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
    st.session_state["rerun"] = True
    st.rerun()


#Reg function
def reg():
    'Already have an Account'
    if st.button('Login Page'):
        st.session_state["reg_in"] = False
        st.session_state["rerun"] = True
        st.rerun()
    new_userid = st.text_input("New Userid")
    new_password = st.text_input("New Password", type="password")
    s=st.text_input("Specialization")
    
        
    if st.button("Register"):
        if collection.find_one({"id": new_userid}) is not None:
            st.warning("The UserID already EXIST.")
        else:
            if new_userid and new_password:
                y={"id":new_userid,"pwd":new_password,"role":'Student',"spec":s,"bal":300}
                collection.insert_one(y)
                st.success('Registered Sucessfully')
            else:
                st.warning("Please enter both userid and password.")
            st.session_state["reg_in"] = False
            st.session_state["rerun"] = True
            st.rerun()



# Login function
def login():
    st.title("Login Page")
    userid = st.text_input("Userid")
    password = st.text_input("Password", type="password")
    'Create an Account'
    if st.button('Registration form'):
        st.session_state["reg_in"] = True
        st.experimental_rerun()
    if st.button("Login"):
            user = collection.find_one({"id": userid})
            if user is not None: 
                if user["pwd"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["userid"] = userid
                    st.session_state["role"] = user["role"]
                    st.session_state["rerun"] = True
                    st.rerun()  # Refresh to show navigation
                else:
                    st.error("Invalid Password")
            else:
                    st.error("Invalid Userid")

       
# Main app interface Student
def maini():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Module", "view Assignments","Payment","Customer Care"])

    if page == "Dashboard":
        st.title("Dashboard")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))

    
    if st.button("Logout"):
        logout()

# Main app interface Instructor
def mains():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Module", "Assignment","Assesment","Payment","Customer Care"])

    if page == "Dashboard":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        documents = p.find({'id':st.session_state['userid']}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({'id':st.session_state['userid'],"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        
    
    if st.button("Logout"):
        logout()

def maina():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page","Instruct Reg", "Course Reg", "Course View","Course Assign","Assign View","Notification"])
    
    if page == "Home Page":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")

    elif page == "Instruct Reg":
        st.title("Instructor Registration")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        new_userid = st.text_input("New Userid")
        new_password = st.text_input("New Password", type="password")
        s=st.text_input("Specialization")
        if st.button("Register"):
            if collection.find_one({"id": new_userid}) is not None:
                st.warning("The UserID already EXIST.")
            else:
                if new_userid and new_password:
                    y={"id":new_userid,"pwd":new_password,"role":'Instructor',"spec":s,"bal":300}
                    collection.insert_one(y)
                    st.success('Registered Sucessfully')
                else:
                    st.warning("Please enter both userid and password.")

    elif page == "Course Reg":
        st.title("Course Registration")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        s=st.text_input("Specialization")
        c=st.text_input("Course")
        exist=list(collection1.find({'spec':s,'course':c}))
        print('exist')
        print(exist)
        if st.button("Insert"):
                if exist ==[]:
                    spec=collection1.find_one({"spec": s})
                    if spec is not None:
                        a=spec['course']
                        a.append(c)
                        collection1.update_one({"spec": s}, {"$set":{'course':a}})
                        st.success(f"Data appended successfully to key: {c}")
                    else:
                        # Create a new document if key does not exist
                            collection1.insert_one({'spec':s,'course':[c]})
                            st.success(f"New key created, data inserted: {s}")
                else:
                        st.warning("The Subject Already Exist")

    elif page == "Course View":
        st.title("Course View")
        st.write("Welcome to the Course View.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        option = st.selectbox("Specialization",(key_values))
        if option:
        # Find all documents where the key exists
            courses = collection1.find({'spec':option})
            if documents:
                st.write(f"Documents with the key '{option}':")
                st.dataframe(courses)  # Display documents in a table format
            else:
                st.write(f"No documents found with the key: {option}")


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