from flask import Flask, Blueprint, render_template, abort, request, session, flash
import db

movie_api = Blueprint('movie_api', __name__)
   
@movie_api.route('/movie', methods=['GET', 'POST'])
def movie():
    movie_name = request.args.get("movie_name").lower()

    query = """
        MATCH (m:Movie)
        WHERE toLower(m.movie_title) = $movie_name
        RETURN m
    """

    node = db.neo4j_driver.session().run(query, movie_name = movie_name).single()
    
    if node is None: abort(404)

    # Ensure movie name has correct capitalization - necessary for INSERT
    movie_name = node["m"]["movie_title"]
    movie_data = dict(node["m"].items())

    db.mysql_cursor.execute('SELECT rating, content FROM Users.Review WHERE MovieName = %s AND email = %s', (movie_name, session["email"]))
    user_review = db.mysql_cursor.fetchone()

    existing_rating = ""
    existing_content = ""

    if user_review is not None:
        existing_rating = user_review[0]
        existing_content = user_review[1]

    if request.method == 'POST':
        new_rating = request.form['rating']
        new_content = request.form['content']

        add_review_to_database(movie_name, existing_rating, existing_content, new_rating, new_content)
        
        existing_rating = new_rating
        existing_content = new_content

    db.mysql_cursor.execute('SELECT * FROM Users.Review WHERE MovieName = %s', (movie_name,)) # Tuple with single value needs trailing comma
    reviews = db.mysql_cursor.fetchall()

    return render_template("movie.html", movie_data = movie_data, reviews = reviews, rating = existing_rating, content = existing_content)

def add_review_to_database(movie_name, existing_rating, existing_content, new_rating, new_content):
    email = session['email']

    # If there is no existing review, INSERT a new one
    if existing_rating == "" and existing_content == "" and new_content != "" and new_rating != "":
        db.mysql_cursor.execute(
            """INSERT INTO 
            Users.Review (MovieName, rating, content, email)
            VALUES (%s,%s,%s,%s)""", 
            (movie_name, new_rating, new_content, email)
        )

        db.mysql_cnx.commit()
        flash('Review Added!')

    # If there is an existing review, UPDATE it
    elif existing_rating != "" and existing_content != "" and new_content != "" and new_rating != "":
        db.mysql_cursor.execute(
            """UPDATE Users.Review
            SET rating = %s, content = %s
            WHERE MovieName = %s AND email = %s""",
            (new_rating, new_content, movie_name, email)
        )

        db.mysql_cnx.commit()
        flash('Review Updated!')

    # If there is an existing review, but the newly submitted review is empty, DELETE the review
    elif existing_content != "" and existing_rating != "" and new_content == "" and new_rating == "":
        db.mysql_cursor.execute(
            """DELETE FROM Users.Review
            WHERE MovieName = %s AND email = %s""", 
            (movie_name, email)
        )

        db.mysql_cnx.commit()
        flash('Review Deleted!')
