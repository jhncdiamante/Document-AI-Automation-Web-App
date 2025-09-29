import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  
DB_PATH = os.path.join(BASE_DIR, "application.db")

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "userdata", "uploads")
    SESSION_TYPE = "sqlalchemy"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_REFRESH_EACH_REQUEST = False
