import os
import sys

# Ensure the project root is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set mock environment variables for test execution
os.environ["OWM_API_KEY"] = "mock_owm_key"
os.environ["GEMINI_API_KEY"] = "mock_gemini_key"
