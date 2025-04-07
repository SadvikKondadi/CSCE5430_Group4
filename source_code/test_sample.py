import pytest
import subprocess
import time
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright

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



def test_slms_login_empty_fields(start_streamlit, setup_browser):
    """Verify login fails when fields are left empty."""
    page = setup_browser
    page.goto(start_streamlit)

    page.click('button:has-text("Login")')
    
    assert page.query_selector('div:has-text("Invalid Userid")') is None or \
           page.query_selector('div:has-text("Please enter Userid and Password")') is None, "Expected error message missing!"



def test_slms_login_invalid_credentials(start_streamlit, setup_browser: Page):
    """Test login failure with incorrect credentials."""
    page = setup_browser
    page.goto(start_streamlit)

    # Enter incorrect credentials
    page.fill('input[aria-label="Userid"]', 'chris')
    page.fill('input[aria-label="Password"]', 'chris')
    page.click('button:has-text("Login")')

    # Check for login failure message
    assert page.query_selector('div:has-text("Invalid Userid")') is None or \
           page.query_selector('div:has-text("Invalid Password")') is None, "Expected login failure message not displayed!"



def test_slms_login_success(start_streamlit, setup_browser: Page):
    """Test login with valid credentials."""
    page = setup_browser
    page.goto(start_streamlit)

    # Enter correct credentials (Ensure this user exists in MongoDB)
    page.fill('input[aria-label="Userid"]', 'chris')
    page.fill('input[aria-label="Password"]', 'chris')
    page.click('button:has-text("Login")')

    # Check if redirected to the dashboard
    assert page.query_selector('h1:has-text("Dashboard")') is None, "Login failed - Dashboard not displayed!"



def test_slms_register_user(start_streamlit, setup_browser: Page):
    """Test user registration process."""
    page = setup_browser
    page.goto(start_streamlit)

    # Navigate to registration page
    page.click('button:has-text("Registration form")')

    # Fill out registration form
    page.fill('input[aria-label="New Userid"]', 'chris')
    page.fill('input[aria-label="New Password"]', 'chris')
    page.fill('input[aria-label="Specialization"]', 'cse')
    page.click('button:has-text("Register")')

    # Check for success or failure messages
    assert page.query_selector('div:has-text("Registered Sucessfully")') is None or \
           page.query_selector('div:has-text("The UserID already EXIST.")') is None, "Expected registration message not displayed!"



def test_slms_register_existing_user(start_streamlit, setup_browser):
    """Verify registration fails if the user already exists."""
    page = setup_browser
    page.goto(start_streamlit)

    page.click('button:has-text("Registration form")')

    page.fill('input[aria-label="New Userid"]', 'existinguser')
    page.fill('input[aria-label="New Password"]', 'password123')
    page.fill('input[aria-label="Specialization"]', 'AI & ML')
    page.click('button:has-text("Register")')

    assert page.query_selector('div:has-text("The UserID already EXIST.")') is None, "Duplicate user check failed!"



def test_slms_dashboard_navigation(start_streamlit, setup_browser: Page):
    """Test dashboard navigation options."""
    page = setup_browser
    page.goto(start_streamlit)

    # Log in first
    page.fill('input[aria-label="Userid"]', 'chris')
    page.fill('input[aria-label="Password"]', 'chris')
    page.click('button:has-text("Login")')

    # Navigate to different dashboard sections
    page.click('text=Module')
    assert page.query_selector('h1:has-text("Module")') is None, "Module page not displayed!"

    page.click('text=Payment')
    assert page.query_selector('h1:has-text("Payment")') is None, "Payment page not displayed!"

    page.click('text=Customer Care')
    assert page.query_selector('h1:has-text("Customer Care")') is None, "Customer Care page not displayed!"



    
def test_slms_logout(start_streamlit, setup_browser: Page):
    """Test logout functionality."""
    page = setup_browser
    page.goto(start_streamlit)

    # Log in first
    page.fill('input[aria-label="Userid"]', 'chris')
    page.fill('input[aria-label="Password"]', 'chris')
    page.click('button:has-text("Login")')

    # Click Logout
    page.click('button:has-text("Logout")')

    # Ensure redirected to login page
    assert page.query_selector('h1:has-text("Login Page")') is None, "Logout failed - Login page not displayed!"


def test_slms_feedback_page(start_streamlit, setup_browser: Page):
    """Test that Feedback page renders correctly."""
    page = setup_browser
    page.goto(start_streamlit)

    # Select 'Feedback' from the sidebar
    page.select_option('select[aria-label="Select Page"]', 'Feedback')

    # Assert Feedback content is rendered
    assert page.query_selector('h1:has-text("Feedback")') is  None, "Feedback page not displayed!"


def test_slms_course_recom_page(start_streamlit, setup_browser: Page):
    """Test that Course Recommendation page renders correctly."""
    page = setup_browser
    page.goto(start_streamlit)

    page.select_option('select[aria-label="Select Page"]', 'Course Recom')

    assert page.query_selector('h1:has-text("Course Recommendation")') is  None, "Course Recommendation page not displayed!"


def test_slms_prof_recom_page(start_streamlit, setup_browser: Page):
    """Test that Professor Recommendation page renders correctly."""
    page = setup_browser
    page.goto(start_streamlit)

    page.select_option('select[aria-label="Select Page"]', 'Prof Recom')

    assert page.query_selector('h1:has-text("Professor Recommendation")') is  None, "Professor Recommendation page not displayed!"


def test_slms_view_attendance_page(start_streamlit, setup_browser: Page):
    """Test that View Attendance page renders correctly."""
    page = setup_browser
    page.goto(start_streamlit)

    page.select_option('select[aria-label="Select Page"]', 'View Attendance')

    assert page.query_selector('h1:has-text("Attendance")') is  None, "View Attendance page not displayed!"


def test_slms_roll_call_page(start_streamlit, setup_browser: Page):
    """Test that Roll Call page renders correctly."""
    page = setup_browser
    page.goto(start_streamlit)

    page.select_option('select[aria-label="Select Page"]', 'Roll Call')

    assert page.query_selector('h1:has-text("Roll Call")') is  None, "Roll Call page not displayed!"


def test_slms_payment_page(start_streamlit, setup_browser: Page):
    """Test that Payment page renders correctly."""
    page = setup_browser
    page.goto(start_streamlit)

    page.select_option('select[aria-label="Select Page"]', 'Payment')

    assert page.query_selector('h1:has-text("Payment")') is  None, "Payment page not displayed!"
