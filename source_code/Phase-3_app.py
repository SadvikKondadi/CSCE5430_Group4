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

def retrival(c,i,o):
    module=[]
    pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
    if pdf_files!=[]:
        for file in pdf_files:
            metadata = file.get("metadata", {})
            if metadata['course']==c and metadata['id']==i and metadata['option']==o:
                module.append(metadata['name'])
    n=m.find({'id':i,'option':o},{"name":1})
    if n is not None:
        for f in n:
            module.append(f['name'])
        selected_filename = st.selectbox("Select a PDF to View",module)

    query = {"metadata.name": selected_filename}
    results = list(db.fs.files.find(query, {"metadata": 1}))
    
    if results !=[]:
        st.write(results[0]['metadata']['description'])
        file_id = results[0]['_id']
        
        pdf_data = fs.get(file_id)
        if results[0]['metadata']['filename'].split(".")[1]=='pdf':
            display_pdf(pdf_data.read())
        st.download_button(label="Download PDF", data=pdf_data.read(), file_name=selected_filename)    
    

    n=m.find_one({"name":selected_filename})
    if n is not None:
        st.write(n['description'])
    return(selected_filename)

def retrivala(c,ins):
    module=[]
    pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
    if pdf_files!=[]:
        for file in pdf_files:
            metadata = file.get("metadata", {})
            if metadata['course']==c and metadata['id']==ins and metadata['option']=='Assesment':
                module.append(metadata['name'])
    
    n=m.find({'id':ins,'option':'Assesment'},{"name":1})
    y=0
    x=0
    if n is not None:
        for f in n:
            module.append(f['name'])
        selected_filename = st.selectbox("Select a PDF to View",module)
        
    if a.find_one({'course':c,'ins':ins,'mod':selected_filename,'id':st.session_state['userid']}) is None:
        
        query = {"metadata.name": selected_filename}
        results = list(db.fs.files.find(query, {"metadata": 1}))

        if results!=[]:
            # Dropdown to select a PDF file
            # Retrieve the PDF file from MongoDB
            file_id = results[0]['_id']
            pdf_data = fs.get(file_id).read()
            if results[0]['metadata']['filename'].split(".")[1]=='pdf':
                display_pdf(pdf_data.read())
            # Convert to bytes and display
            st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename)

            if results[0]['metadata']['choice']=='Descriptive':
                st.write(results[0]['metadata']['description'])
                ans=st.text_area('Enter the Answer')

                ansd.insert_one({'id':st.session_state["userid"],'course':c,'ins':ins,'question':results[0]['metadata']['description'],'ans':ans,'flag':results[0]['metadata']['flag']})
                embedding1 = get_embedding(ans)
                if results[0]['metadata']['flag']:
                    embedding2 = get_embedding(results[0]['metadata']['ans'])
                    similarity_score = cosine_similarity(embedding1, embedding2)
                    x=1
            if results[0]['metadata']['choice']=='MCQ':
                ans=st.radio(results[0]['metadata']['description'],[results[0]['metadata']['a']])

            if results[0]['metadata']['choice']=='More than One Answer MCQ':
                ans=[]
                for i in results[0]['metadata']['a']:
                    ci=st.checkbox(i)
                    if ci==True:
                        ans.append(i)

            if results[0]['metadata']['choice']=='True or False':
                ans=st.radio(results[0]['metadata']['description'],[True,False])
            y=1
            
        n=m.find_one({"name":selected_filename})

        if n is not None:
            if n['option']=='Assesment':
                if n['choice']=='Descriptive':
                    st.write(n['description'])
                    ans=st.text_area('Enter the Answer')
                    ansd.insert_one({'id':st.session_state["userid"],'course':c,'ins':ins,'question':n['description'],'ans':ans,'flag':n['flag']})
                    embedding1 = get_embedding(ans)
                    if n['flag']:
                        embedding2 = get_embedding(n['ans'])
                        similarity_score = cosine_similarity(embedding1, embedding2)
                        x=1

                if n['choice']=='MCQ':
                    ans=st.radio(n['description'],n['a'])
                if n['choice']=='More than One Answer MCQ':
                    ans=[]
                    for i in n['a']:
                        ci=st.checkbox(i)
                        if ci:
                            ans.append(i)
                if n['choice']=='True or False':
                    ans=st.radio(n['description'],['True','False'])

        if st.button('submit'):
            a.insert_one({'course':c,'ins':ins,'mod':selected_filename,'id':st.session_state['userid']})
            st.session_state.mark=st.session_state.mark+1

            if y==1:
                if results[0]['metadata']['flag']:
                    if x==0:
                        if ans==results[0]['metadata']['ans']:
                            st.session_state.mar=st.session_state.mar+1

                            st.success(f'✅Correct Score:{st.session_state.mar}')
                        else:
                            st.error('Wrong')
                    else:
                        st.session_state.mar=st.session_state.mar+similarity_score
                        st.success(f'✅Correct Score:{results[0]["metadata"]["tmark"]*similarity_score}')
                else:
                    st.warning('Will be graded by the Instructor soon')
            else:
                if n['flag']:
                    if x==0:
                        if ans==n['ans']: 
                            
                            st.session_state.mar=st.session_state.mar+1

                            st.success(f'✅Correct Score:{st.session_state.mar}')
                        else:
                            st.error('Wrong')
                    else:
                        st.session_state.mar=st.session_state.mar+similarity_score
                        st.success(f'✅Correct Score:{n["tmark"]*similarity_score}')
                else:
                    st.warning('Will be graded by the Instructor soon')
            
                
            if st.session_state.mark==len(module):
                st.title(f'Total Score: {st.session_state.mar}')
                ma=p.find_one({'course':c,'instructor':ins},{'_id':0,'m':1})
                marks=st.session_state.mar+ma['m']
                st.session_state.exam=st.session_state.exam+1
                ass.insert_one({'Exam':f'Exam{st.session_state.exam}','course':c,'instructor':ins,'student':st.session_state['userid'],'Marks':st.session_state.mar})
                p.update_one({'course':c,'instructor':ins},{'$set':{'m':marks}})
                st.session_state.mar=0
                st.session_state.mark=0

    else:
        st.warning('Already Answered')

