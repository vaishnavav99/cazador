from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient
import json

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize database
db = SQLAlchemy(app)

# Load the OAuth 2.0 client secrets file
with open('client_secrets.json') as f:
    google_client_info = json.load(f)['web']

GOOGLE_CLIENT_ID = google_client_info['client_id']
GOOGLE_CLIENT_SECRET = google_client_info['client_secret']
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Import routes
from routes import *

from flask_wtf.csrf import CSRFProtect
# CSRF protection
csrf = CSRFProtect(app)