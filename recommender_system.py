#=========================================
# File name: recommender_system.py
# Author: Chongye Wang
# Function: This file handles recommender system.
#=========================================

from flask import Flask, Blueprint, render_template, flash, request, session, redirect, url_for, abort
from mysql.connector import errorcode
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash
import db
from sklearn.cluster import KMeans
import numpy as np
import random
from sklearn.preprocessing import normalize
import heapq
from sklearn.metrics.pairwise import cosine_similarity


recommend_api = Blueprint('recommend_api', __name__)


def generate_users():
    """
    Batch processing of generating users.
    """
    for i in range(200):
        first_name = str(i)
        last_name = "user"
        email = "user" + str(i) + "@gmail.com"
        password = "test"
        db.mysql_cursor.execute(
            """INSERT INTO 
            Users.User (first_name, last_name, password, email)
            VALUES (%s,%s,%s,%s)""", 
            (first_name, last_name, generate_password_hash(password), email)
        )
    db.mysql_cnx.commit()


def generate_ratings():
    """
    Batch processing of generating user ratings.
    For selected users in the database, generate ratings 
    for 1 to 30 movies.
    """
    db.mysql_cursor.execute("SELECT email FROM Users.User")
    users = db.mysql_cursor.fetchall()
    users = list(set([random.choice(users) for _ in range(int(len(users) / 4))]))

    query = """
        MATCH (m:Movie) RETURN m
    """

    all_movies = db.neo4j_driver.session().run(query)
    if all_movies is None: abort(404)
    movies = []
    for movie in all_movies:
        movies.append(dict(movie.items())["m"]["movie_title"])

    for user_tuple in users:
        user = user_tuple[0]
        random_movies = list(set([random.choice(movies) for _ in range(random.randint(1, 30))]))
        for movie in random_movies:
            db.mysql_cursor.execute(
                """SELECT * FROM Users.Review where MovieName = %s AND email = %s""", 
                (movie, user)
            )

            if db.mysql_cursor.fetchall(): continue
            rating = random.randint(1, 10)
            if rating <= 3:
                content = "Bad movie"
            elif rating > 3 and rating <= 6:
                content = "Average"
            else:
                content = "Nice movie"

            db.mysql_cursor.execute(
                """INSERT INTO 
                Users.Review (MovieName, rating, content, email)
                VALUES (%s,%s,%s,%s)""", 
                (movie, rating, content, user)
            )

    db.mysql_cnx.commit()


def initilize_user_ratings_model():
    """
    Initialize the user ratings matrix
    """
    genres = [
        "Action",
        "Adventure",
        "Drama",
        "Animation",
        "Comedy",
        "Mystery",
        "Crime",
        "Biography",
        "Fantasy",
        "Documentary",
        "Sci-Fi",
        "Horror",
        "Romance",
        "Thriller",
        "Family",
        "Music",
        "Western",
        "Musical",
        "Film-Noir",
        "History",
        "War",
        "Sport",
        "Short",
        "News"
    ]

    user_ratings_matrix = {}

    db.mysql_cursor.execute("SELECT email FROM Users.User")
    
    all_users = db.mysql_cursor.fetchall()
    for user in all_users:
        user_ratings_matrix[user[0]] = {}
        for genre in genres:
            user_ratings_matrix[user[0]][genre] = {}
            user_ratings_matrix[user[0]][genre]["rating_num"] = 0.0
            user_ratings_matrix[user[0]][genre]["rating_average"] = 0.0

    return user_ratings_matrix


def add_review_to_model(user_ratings_matrix):
    """
    Add the reviews from the database to matrix
    """
    db.mysql_cursor.execute("SELECT * FROM Users.Review")
    if(db.mysql_cursor.fetchone() is not None): 
        db.mysql_cursor.execute(
            """SELECT email, MovieName, rating FROM
            Users.Review""", 
            
        )
        all_reviews = db.mysql_cursor.fetchall()
        for review in all_reviews:
            username = review[0]
            movie_name = review[1].lower()
            movie_rating = review[2]
            query = """
                MATCH (m:Movie)
                WHERE toLower(m.movie_title) = $movie_name
                RETURN m
            """
            node = db.neo4j_driver.session().run(query, movie_name = movie_name).single()
            if node is None: abort(404)
            movie_name = node["m"]["movie_title"]
            movie_data = dict(node["m"].items())
            for genre in movie_data["genres"]:
                rating_num = user_ratings_matrix[username][genre]["rating_num"]
                rating_average = user_ratings_matrix[username][genre]["rating_average"]
                user_ratings_matrix[username][genre]["rating_num"] += 1.0
                user_ratings_matrix[username][genre]["rating_average"] = (rating_num * rating_average + movie_rating) / (rating_num + 1.0)


def normalize_matrix(user_ratings_matrix):
    """
    Normalize the user rating matrix
    """
    normalized_matrix = {}
    for user in user_ratings_matrix:  
        normalized_matrix[user] = normalize([[user_ratings_matrix[user][genre]["rating_average"] for genre in user_ratings_matrix[user]]])
    return normalized_matrix


def get_k_similar_users(k, target_user, normalized_matrix):
    """
    Select k nearest users to the target user using cosine similarity.
    """
    if k >= len(normalized_matrix): 
        return None
    priority_queue = []
    target_array = normalized_matrix[target_user].reshape(1, normalized_matrix[target_user].size)
    for user in normalized_matrix:
        if user == target_user: continue
        current_array = normalized_matrix[user].reshape(1, normalized_matrix[user].size)
        similarity = -cosine_similarity(target_array, current_array)
        heapq.heappush(priority_queue, (similarity, user))
    k_nearest_users = []
    while k > 0:
        k_nearest_users.append(heapq.heappop(priority_queue))
        k -= 1
    return k_nearest_users



@recommend_api.route('/recommend', methods=['GET', 'POST'])
def recommend():
    """
    The main function of recommending potential relations to the current user.
    """

    # Initialize the user-rating matrix
    user_ratings_matrix = initilize_user_ratings_model()
    
    # Import reviews from mysql to the user-rating matrix
    add_review_to_model(user_ratings_matrix)
    
    # Normalize the user-rating matrix
    normalized_matrix = normalize_matrix(user_ratings_matrix)
    
    # Retrieve the k nearest users
    k_nearest_users = get_k_similar_users(3, "test5@gmail.com", normalized_matrix)

    #### Test data. To be removed ####
    print(k_nearest_users)
    print(normalized_matrix["test5@gmail.com"])
    for user in k_nearest_users:
        print(normalized_matrix[user[1]])
    #### Test data. To be removed ####

    return render_template('recommend.html')


