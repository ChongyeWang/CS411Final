from flask import Flask, Blueprint, render_template, flash, request, session, redirect, url_for, abort
from mysql.connector import errorcode
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash
import db

def generate_users():
    """
        Adds test users to the database.
        A user is created for the below names,
        with an email of first_last@gmail.com and a password of "password".
        Users are inserted into the SQL and Neo4j databases.
    """
    names = [
        "Gloria Perez",
        "Stephanie Hall",
        "Jack Williams",
        "Tammy White",
        "Wanda Ramirez",
        "Richard Morgan",
        "Steve Russell",
        "Sara Hill",
        "Stephen Richardson",
        "Adam Cooper",
        "Catherine Parker",
        "Arthur Stewart",
        "Elizabeth Cox",
        "Pamela Mitchell",
        "Christina Hughes",
        "Susan Turner",
        "Craig Taylor",
        "Fred Powell",
        "Ronald Rodriguez",
        "Ashley Flores",
        "John Lee",
        "Patrick Johnson",
        "Helen Gonzales",
        "Bruce Murphy",
        "Nicholas Torres",
        "Ernest Ross",
        "Kenneth Sanders",
        "Roy Wilson",
        "Janet Jackson",
        "Eric Bryant",
        "Bonnie Thompson",
        "Lawrence Collins",
        "Ruby Gonzalez",
        "Jimmy Henderson",
        "Heather Perry",
        "Frank Harris",
        "Carolyn Evans",
        "Beverly Howard",
        "Marie Clark",
        "Douglas James",
        "Carlos Bailey",
        "Donald Washington",
        "Linda Green",
        "Mary Rogers",
        "Diane Adams",
        "Peter Ward",
        "Keith Rivera",
        "Sharon Brown",
        "Virginia Edwards",
        "Paula Patterson",
        "Gary Jones",
        "Roger Young",
        "Chris Garcia",
        "Matthew Foster",
        "Marilyn Gray",
        "Teresa Reed",
        "Norma Roberts",
        "Harry Butler",
        "Betty Peterson",
        "Brenda Sanchez",
        "Raymond Smith",
        "Larry Martin",
        "Victor Bennett",
        "Albert Martinez",
        "Irene King",
        "Dorothy Walker",
        "Amanda Campbell",
        "Rose Diaz",
        "Shawn Kelly",
        "Jacqueline Lewis",
        "Judy Miller",
        "Benjamin Thomas",
        "Clarence Nelson",
        "Brian Alexander",
        "Annie Cook",
        "Judith Wood",
        "Bobby Watson",
        "Martha Long",
        "Barbara Lopez",
        "Theresa Brooks",
        "Kathleen Phillips",
        "Jonathan Davis",
        "Kelly Jenkins",
        "Jane Anderson",
        "Steven Hernandez",
        "Jennifer Price",
        "Dennis Bell",
        "Martin Morris",
        "Lillian Carter",
        "Cheryl Robinson",
        "Diana Simmons",
        "Joan Allen",
        "Samuel Barnes",
        "David Scott",
        "Willie Baker",
        "Mark Coleman",
        "Janice Moore",
        "Phillip Griffin",
        "Timothy Wright"
    ]

    for name in names:
        first_name = name.split(" ")[0]
        last_name = name.split(" ")[1]
        email = first_name + "_" + last_name + "@gmail.com"
        email = email.lower()
        password = "password"
        db.mysql_cursor.execute(
            """INSERT INTO 
            Users.User (first_name, last_name, password, email)
            VALUES (%s, %s, %s, %s)""", 
            (first_name, last_name, generate_password_hash(password), email)
        )

        db.neo4j_driver.session().run("CREATE (u:User {email: $email})", email=email)
    db.mysql_cnx.commit()


def generate_ratings(users_count, reviews_count):
    """
        Selects users_count users at random from the database and adds reviews_count
        random reviews for each chosen user for random movies.
    """

    db.mysql_cursor.execute("SELECT email FROM Users.User")
    users = db.mysql_cursor.fetchall()
    random_users = random.sample(users, users_count)

    all_movies = db.neo4j_driver.session().run("MATCH (m:Movie) RETURN m.movie_title AS movie_title")
    movie_titles = [movie["movie_title"] for movie in all_movies]
    
    for user_tuple in random_users:
        user = user_tuple[0]
        random_movies = random.sample(movie_titles, reviews_count)

        for movie in random_movies:
            db.mysql_cursor.execute(
                """SELECT * FROM Users.Review where MovieName = %s AND email = %s""", 
                (movie, user)
            )

            if db.mysql_cursor.fetchall(): continue # User has already reviewed movie

            rating = random.randint(1, 10)
            
            if rating <= 3:
                content = "Bad movie"
            elif rating <= 6:
                content = "Average"
            else:
                content = "Nice movie"

            db.mysql_cursor.execute(
                """INSERT INTO 
                Users.Review (MovieName, rating, content, email)
                VALUES (%s, %s, %s, %s)""", 
                (movie, rating, content, user)
            )

    db.mysql_cnx.commit()