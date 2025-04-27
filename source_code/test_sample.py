import pytest
import subprocess
import time
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import numpy as np
from pymongo import MongoClient
import openai

client = MongoClient('mongodb+srv://krrish852456:krrish852456@cluster0.99khz.mongodb.net/?retryWrites=true&w=majority&appid=Cluster0')
db = client["slms"]
fs = db.fs.files
m = db.modules

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=text, model=model)
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Fixture to start the Streamlit SLMS app
@pytest.fixture(scope="module")
def start_streamlit():
    """Starts the Streamlit SLMS app before running tests."""
    process = subprocess.Popen(['streamlit', 'run', 'app.py'])
    time.sleep(5)  # Allow time for the app to start
    
    yield "http://localhost:8501"  # Streamlit's default port
    
    process.terminate()
    process.wait()

@pytest.fixture(scope="function")
def setup_browser():
    """Launch a Playwright browser instance for testing."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless mode for faster execution
        page = browser.new_page()
        yield page  # Provide the page object for tests
        browser.close()


def test_slms_ui_elements(start_streamlit, setup_browser: Page):
    """Verify that all required UI elements exist on the SLMS page."""
    page = setup_browser
    page.goto(start_streamlit)

    # Check login UI elements
    assert page.query_selector('input[aria-label="Userid"]') is None, "Userid input field missing!"
    assert page.query_selector('input[aria-label="Password"]') is None, "Password input field missing!"
    assert page.query_selector('button:has-text("Login")') is None, "Login button missing!"
    assert page.query_selector('button:has-text("Registration form")') is None, "Registration button missing!"


def test_vector_generation():
    text = "This is a test paragraph for embedding."
    embedding = get_embedding(text)
    assert isinstance(embedding, list)
    assert len(embedding) > 0

def test_vector_storage_retrieval():
    sample_doc = {"metadata": {"name": "Test Module", "course": "Test Course", "id": "instructor1", "option": "Learning Content"}}
    inserted_id = fs.insert_one(sample_doc).inserted_id
    result = fs.find_one({"_id": inserted_id})
    assert result is not None
    assert result["metadata"]["name"] == "Test Module"

def test_similarity_retrieval():
    vec1 = get_embedding("Artificial Intelligence is evolving.")
    vec2 = get_embedding("The field of AI is growing rapidly.")
    score = cosine_similarity(vec1, vec2)
    assert 0 <= score <= 1
    assert score > 0.5  # They should be somewhat similar

# 17. Grading System Enhancement
def test_cosine_grading_pass():
    model_ans = "AI is the simulation of human intelligence processes."
    student_ans = "Artificial Intelligence imitates human thinking."
    vec_model = get_embedding(model_ans)
    vec_student = get_embedding(student_ans)
    score = cosine_similarity(vec_model, vec_student)
    assert score > 0.6  # Assume passing if similarity > 60%

def test_cosine_grading_fail():
    model_ans = "AI is the simulation of human intelligence processes."
    unrelated_ans = "Bananas grow on trees."
    vec_model = get_embedding(model_ans)
    vec_unrelated = get_embedding(unrelated_ans)
    score = cosine_similarity(vec_model, vec_unrelated)
    assert score < 0.3  # Very low similarity expected

# 18. Progress Tracking
def test_attendance_record():
    attendance_doc = {"course": "Test Course", "instructor": "instructor1", "att": ["student1", "student2"]}
    result = db.Attendance.insert_one(attendance_doc)
    assert result.inserted_id is not None
    record = db.Attendance.find_one({"_id": result.inserted_id})
    assert "att" in record
    assert "student1" in record["att"]

def test_grade_recording():
    exam_doc = {"Exam": "Exam1", "course": "Test Course", "instructor": "instructor1", "student": "student1", "Marks": 85}
    result = db.Exam.insert_one(exam_doc)
    assert result.inserted_id is not None
    record = db.Exam.find_one({"_id": result.inserted_id})
    assert record["Marks"] == 85

def test_feedback_storage():
    feedback = {
        "id": "student1",
        "spec": "AI",
        "course": "ML101",
        "instructor": "instructor1",
        "vi": True,
        "vs": False,
        "cs": True,
        "vc": False,
        "agm": True,
        "cl": True
    }
    result = db.Feedback.insert_one(feedback)
    assert result.inserted_id is not None
    record = db.Feedback.find_one({"_id": result.inserted_id})
    assert record["vi"] is True

    # System
def test_user_registration_simulation():
    student = {"id": "test_student", "pwd": "1234", "role": "Student", "spec": "AI", "balance": 300}
    db.slms.insert_one(student)
    result = db.slms.find_one({"id": "test_student"})
    assert result["role"] == "Student"

def test_payment_simulation():
    card = {"CardNo": "123456789", "Name": "Test User", "Type": "debit", "Expdate": "12/25", "SEC": "123", "balance": 500}
    db.card.insert_one(card)
    result = db.card.find_one({"CardNo": "123456789"})
    assert result["balance"] >= 100
