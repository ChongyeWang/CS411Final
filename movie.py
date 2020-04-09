from flask import Flask, Blueprint, render_template, abort
import db

movie_api = Blueprint('movie_api', __name__)

@movie_api.route('/movie/<movie_name>')
def movie(movie_name):
    movie_name = movie_name.lower()
    query = """
        MATCH (m:Movie)
        WHERE toLower(m.movie_title) = $movie_name
        RETURN m
    """

    node = db.neo4j_driver.session().run(query, movie_name = movie_name).single()
    
    if node is not None:
        movie_data = dict(node["m"].items())

        db.mysql_cursor.execute('SELECT * FROM Users.Review WHERE MovieName = %s', (movie_name,)) # Tuple with single value needs trailing comma
        reviews = db.mysql_cursor.fetchall()

        return render_template("movie.html", movie_data = movie_data, reviews = reviews)

    abort(404)