# app/config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mliu')  # Default for development
    TEMPLATES_AUTO_RELOAD = True