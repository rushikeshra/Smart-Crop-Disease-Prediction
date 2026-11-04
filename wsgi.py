from app import app, load_ml_model, load_crop_recommender
from database.db import init_db

init_db()
load_ml_model()
load_crop_recommender()