from dotenv import load_dotenv
import os

load_dotenv('config/config.env')
ADMIN_ID = os.getenv('ADMIN_ID')