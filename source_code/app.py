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

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="600"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    #binary_data = pdf_file.getvalue()
    #pdf_viewer(input=binary_data,width=700)


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