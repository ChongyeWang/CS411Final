from flask import Flask, Blueprint, render_template, abort, request, session, flash
from recommender_system import *
import db
import numpy as np
import os
import time
import threading


homepage_api = Blueprint('homepage_api', __name__)

movies_query = "MATCH (m:Movie) RETURN m.movie_title"
movies = db.neo4j_driver.session().run(movies_query).values()
movies = [movie[0] for movie in movies]

matrix_filename = "recommendation_matrix.npy"

try:
    recommendation_matrix = np.load(matrix_filename, allow_pickle=True).item()
except:
    generate_recommendation_matrix()


@homepage_api.route('/')
def index():
    if not session.get("email"):
        return render_template("index_not_logged_in.html")

    update_recommendation_matrix()
    num_recommendations = 5
    recommendations = get_recommended_friends(
        num_recommendations, recommendation_matrix)
    recommendations = db.get_user_data(recommendations)

    friends = db.get_all_friends(session["email"])
    friends = db.get_user_data(friends)

    return render_template("index_logged_in.html", movies=movies, recommendations=recommendations, friends=friends)


def update_recommendation_matrix():
    """
    If the recommendation matrix is at least one day old, it will be updated.
    This update occurs in a new thread. The file modification time is updated to prevent
    multiple updates from occurring simultaneously.
    """
    SECONDS_TO_DAYS = 60 * 60 * 24
    last_modification_time = os.path.getmtime(matrix_filename)
    now = time.time()
    days_elapsed = (now - last_modification_time) / SECONDS_TO_DAYS

    if days_elapsed < 1:
        os.utime(matrix_filename)
        tid = threading.Thread(target=generate_recommendation_matrix)
