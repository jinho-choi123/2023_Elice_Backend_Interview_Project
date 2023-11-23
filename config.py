import os 
from dotenv import load_dotenv

## import secrets from dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".config", ".env"))
