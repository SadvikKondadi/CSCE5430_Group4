import streamlit as st
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import gridfs

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

def mainc():
    st.session_state.notif=[]
    llm=ChatOpenAI(api_key='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',                            #st.secrets["OPEN_API_KEY"]
                   model_name='gpt-4o',
                   temperature=0.0)
    prompt_template='''If any actionable prompt is given the state yes else give the response.   
    Text:
    {context}'''
    PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context"])
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! Welcome to customer care. How Can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
    
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        chain = LLMChain(llm=llm, prompt=PROMPT)
        answer=chain.run(prompt)
        if re.search(r'\bYes\b', answer):
            cust.insert_one({'id':st.session_state["userid"],'query':prompt})
            st.chat_message("assistant").write("Notified to the Admin, He will get back to you soon...")
        else:
            prompt_template='''Accept the queries as a customer care and give an accuarte reply.   
            Text:
            {context}'''
            PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context"])
            chain = LLMChain(llm=llm, prompt=PROMPT).run(prompt)
            st.session_state.messages.append({"role": "assistant", "content": chain})
            st.chat_message("assistant").write(chain)


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

    elif page == "Customer Care":
        st.title("Customer Care")
        mainc()

    
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
        
    elif page == "Customer Care":
        st.title("Customer Care")
        mainc() 

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

    elif page == "Course Assign":
        st.title("Course Registration")
        st.write("Welcome to the Course page.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
        key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values[0])

        docum = collection.find({"role":"Instructor","spec":s}, {"id": 1, "_id": 0})
        key_values = [doc['id'] for doc in docum if 'id' in doc]
        i = st.selectbox("Instructor",(key_values))

        if st.button("Insert"):
            spec=collection2.find_one({"spec": s,'course':c})
            if  spec is not None:
                # Append new values to the existing array
                a=spec['Instructor']
                a.append(i)
                collection2.update_one({"spec": s,'course':c}, {"$set":{'Instructor':a}})
                st.success(f"Data appended successfully to key: {c}")
            else:
                # Create a new document if key does not exist
                collection2.insert_one({'spec':s,'course':c,'Instructor':[i]})
                st.success(f"New key created, data inserted: {s}")


    elif page == "Assign View":
            st.title("Assign View")
            st.write("Welcome to the Assign View.")
            documents = collection1.find({}, {"spec": 1, "_id": 0})
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
            option = st.selectbox("Specialization",(key_values))
            if option:
            # Find all documents where the key exists
                courses = collection2.find({'spec':option})
                if documents:
                    st.write(f"Documents with the key '{option}':")
                    st.dataframe(courses)  # Display documents in a table format
                else:
                    st.write(f"No documents found with the key: {option}")

    elif page == "Assign View":
        st.title("Assign View")
        st.write("Welcome to the Assign View.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        option = st.selectbox("Specialization",(key_values))
        if option:
        # Find all documents where the key exists
            courses = collection2.find({'spec':option})
            if documents:
                st.write(f"Documents with the key '{option}':")
                st.dataframe(courses)  # Display documents in a table format
            else:
                st.write(f"No documents found with the key: {option}")

    elif page == "Notification":
        st.title("Customer Service")
        c=cust.find({},{'query':1,'id':1,'_id':0})
        print('c')
        print(c)
        if c!=[]:
            i=[i for i in c]
            print(i)
            print('i')
            for j in i:
                if st.button(f"{j['id']}:{j['query']}"):
                    cust.delete_one({'id':j['id'],'query':j['query']})

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