import streamlit as st
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from pymongo import MongoClient
import gridfs
import base64
import io
from collections import Counter
from collections import defaultdict
import pandas as pd
import numpy as np
import openai

# Simulated user database
client = MongoClient('mongodb+srv://krrish852456:krrish852456@cluster0.99khz.mongodb.net/?retryWrites=true&w=majority&appid=Cluster0')

db = client["slms"]
dba=client['assign']
collection = db["slms"]
collection1 = db["Subjects"]
collection2 = db["Instructor"]
cust = db["Customer Care"]
assign=db["assign"]
sum=db["Summary"]
m=db["modules"]
p=db["payment"]
a=db["Attempt"]
ass=db["Exam"]
ab=db["Attendance"]
ag=db["AgAttendance"]
f=db["Feedback"]
carddata=db["card"]
ansd=db["Ansd"]
fs = gridfs.GridFS(db)
fsa = gridfs.GridFS(dba)
# Session state initialization
if "reg_in" not in st.session_state:
    st.session_state["reg_in"] = False
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
if "messages" not in st.session_state:
    st.session_state.messages = {}  # Store chat history per user
if "admin_joined" not in st.session_state:
    st.session_state.admin_joined = {}
if 'mar' not in st.session_state:
    st.session_state.mar=0
if 'mark' not in st.session_state:
    st.session_state.mark=0
if 'exam' not in st.session_state:
    st.session_state.exam=0
if 'descriptive' not in st.session_state:
    st.session_state.descriptive=0
if 'call' not in st.session_state:
    st.session_state.call=0
if "ms" not in st.session_state:
    st.session_state["ms"] = [{"role": "assistant", "content": "Enter your profession to get course recommendations:"}]

#Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
    st.session_state["rerun"] = True
    st.rerun()

openai.api_key = st.secrets["OPEN_API_KEY"]

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

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
                y={"id":new_userid,"pwd":new_password,"role":'Student',"spec":s,"balance":300}
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

