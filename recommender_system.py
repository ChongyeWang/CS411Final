import db
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import random
import heapq
import numpy as np
from numpy import *
from flask import *


def initilize_user_ratings_model():
    """
    Initialize the user ratings matrix
    """

    query = "MATCH (m:Movie) UNWIND m.genres as genres RETURN COLLECT(DISTINCT genres) AS genres"
    genres = node = db.neo4j_driver.session().run(query).single()["genres"]

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


def add_reviews_to_model(user_ratings_matrix):
    """
    Add the reviews from the database to matrix
    """
    db.mysql_cursor.execute("SELECT * FROM Users.Review")
    if(db.mysql_cursor.fetchone() is not None):
        db.mysql_cursor.execute(
            """SELECT email, MovieName, rating FROM
            Users.Review"""
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
            node = db.neo4j_driver.session().run(query, movie_name=movie_name).single()
            if node is None:
                abort(404)
            movie_name = node["m"]["movie_title"]
            movie_data = dict(node["m"].items())
            for genre in movie_data["genres"]:
                rating_num = user_ratings_matrix[username][genre]["rating_num"]
                rating_average = user_ratings_matrix[username][genre]["rating_average"]
                user_ratings_matrix[username][genre]["rating_num"] += 1.0
                user_ratings_matrix[username][genre]["rating_average"] = (
                    rating_num * rating_average + movie_rating) / (rating_num + 1.0)


def normalize_matrix(user_ratings_matrix):
    """
    Normalize the user rating matrix
    """
    normalized_matrix = {}
    for user in user_ratings_matrix:
        normalized_matrix[user] = normalize(
            [[user_ratings_matrix[user][genre]["rating_average"] for genre in user_ratings_matrix[user]]])
    return normalized_matrix


def get_k_similar_users(k, target_user, normalized_matrix):
    """
    Select k nearest users to the target user using cosine similarity.
    """
    if k >= len(normalized_matrix):
        return None
    priority_queue = []
    k_nearest_users = []

    try:
        target_array = normalized_matrix[target_user].reshape(
            1, normalized_matrix[target_user].size)
    except:
        return []

    for user in normalized_matrix:
        if user == target_user:
            continue
        current_array = normalized_matrix[user].reshape(
            1, normalized_matrix[user].size)
        similarity = -cosine_similarity(target_array, current_array)
        heapq.heappush(priority_queue, (similarity, user))
    while k > 0:
        k_nearest_users.append(heapq.heappop(priority_queue)[1])
        k -= 1

    return k_nearest_users


def generate_recommendation_matrix():
    user_ratings_matrix = initilize_user_ratings_model()
    add_reviews_to_model(user_ratings_matrix)

    normalized_matrix = normalize_matrix(user_ratings_matrix)
    filename = "./recommendation_matrix"
    np.save(filename, normalized_matrix)


def get_recommended_friends(num_recommendations, recommendation_matrix):
    """
        Returns a list of emails of recommended friends.
        The best num_recommendations suggestions will be returned. If a user is
        already a friend, they will be ignored. The result may contain fewer
        than num_recommendations users.
    """

    recommended_friends = get_k_similar_users(
        num_recommendations, session["email"], recommendation_matrix)

    current_friends = db.get_all_friends(session["email"])
    recommendations = list(set(recommended_friends) - set(current_friends))

    return recommendations
