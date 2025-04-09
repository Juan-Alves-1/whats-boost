from fastapi.templating import Jinja2Templates
import os

TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
templates = Jinja2Templates(directory=TEMPLATES_DIR)