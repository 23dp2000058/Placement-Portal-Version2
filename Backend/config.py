import os

class LocalDevelopmentConfig:
    # --- Existing DB and Security configs ---
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"
    SECURITY_PASSWORD_SALT = "your-salt"
    
    # Required for Token Auth (Flask-Security-Too)
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    WTF_CSRF_ENABLED = False 

    # --- File Upload Configurations ---
    # Unified naming to match your Service files
    UPLOAD_FOLDER_RESUMES = os.path.join('static', 'uploads', 'resumes')
    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'offer_letters') # Matches company_service.py
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}
    
    # --- Caching & Background Jobs (Mandatory) ---
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    
    # Celery Config
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    CELERY_TIMEZONE = "Asia/Kolkata"