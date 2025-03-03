import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")