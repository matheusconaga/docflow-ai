import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
