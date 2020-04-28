from flask import Flask, Blueprint, render_template, abort, request, session, flash
import db

profile_api = Blueprint('profile_api', __name__)
   
@profile_api.route('/profile', methods=['GET', 'POST'])
def profile():
    db.mysql_cursor.execute('SELECT email, first_name, last_name FROM Users.User WHERE email = %s', (session["email"],))
    user_info = db.mysql_cursor.fetchall()
    db.mysql_cursor.execute('SELECT rating, content, MovieName FROM Users.Review WHERE email = %s', (session["email"],))
    user_reviews = db.mysql_cursor.fetchall()
    print(user_reviews)
    print(user_reviews)

    rating_num = len(user_reviews)
    rating_average = 0

    if rating_num > 0:
        rating_average = round(sum([i[0] for i in user_reviews]) / rating_num, 1)

    return render_template("profile.html", user_info=user_info, user_reviews=user_reviews, rating_num=rating_num, rating_average=rating_average)
