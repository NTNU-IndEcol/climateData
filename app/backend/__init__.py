from flask import Flask
import os

app = Flask(__name__)

# Import routes
from app import routes
