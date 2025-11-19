import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MAPS_API_KEY = os.getenv("MAPS_API_KEY")
# You can add other API keys here, for example:
# REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
# REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
# REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Model Names
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-lite-latest")

# Map Settings
DEFAULT_MAP_CENTER = [34.0522, -118.2437] # Los Angeles
DEFAULT_MAP_ZOOM = 11

# Simulation Settings
SIMULATION_SPEED_SECONDS = 1.0

# Verification Threshold
VERIFICATION_THRESHOLD = 70
