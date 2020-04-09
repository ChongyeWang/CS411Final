from flask import Flask, Blueprint, render_template, abort, request, session
import db
from wtforms import Form, TextField, IntegerField, TextAreaField, validators, StringField, SubmitField

movie_api = Blueprint('movie_api', __name__)


class ReviewForm(Form):
    rating = IntegerField('Rating:', validators=[validators.required()])
    content = TextField('Content:', validators=[validators.required()])
    

@movie_api.route('/movie', methods=['GET', 'POST'])
def movie():
    movie_name = request.args.get("movie_name").lower()
    print(movie_name)
    print(session)
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

        # return render_template("movie.html", movie_data = movie_data, reviews = reviews, form=form)


    form = ReviewForm(request.form)

    if request.method == 'POST':
        rating = request.form['rating']
        content = request.form['content']
        email = session['email']

        if form.validate():
            print(movie_name)
            print(rating)
            print(content)
            print(email)
            db.mysql_cursor.execute(
                """INSERT INTO 
                Users.Review (MovieName, rating, content, email)
                VALUES (%s,%s,%s,%s)""", 
                (movie_name, rating, content, email)
            )
            db.mysql_cnx.commit()

        return render_template("movie.html", movie_data = movie_data, reviews = reviews, form=form)

    return render_template("movie.html", movie_data = movie_data, reviews = reviews, form=form)

    abort(404)
