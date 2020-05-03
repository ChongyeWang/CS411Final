from flask import Flask, Blueprint, render_template, flash, request, session, redirect, url_for
from mysql.connector import errorcode
from wtforms import *
from wtforms.validators import *
from wtforms.fields.html5 import *
from werkzeug.security import check_password_hash, generate_password_hash
import db

register_api = Blueprint('register_api', __name__)

class RegistrationForm(Form):
    first_name = StringField('First Name:', [InputRequired(message = "Little short for an email address?")])
    last_name = StringField('Last Name:', [InputRequired(message = "Please enter your last name.")])
    email = EmailField('Email:', [Email(message = "Please enter your email address.")])
    password = PasswordField('Password:', [Length(min = 8, message = "Please enter a password of at least eight characters.")])
    confirm_password = PasswordField('Confirm Password:', [InputRequired(message = "Please confirm your password."), EqualTo('password', message = "The passwords do not match.")])
    

@register_api.route('/register', methods=['GET', 'POST'])
def register():
    """This function handles user registration."""
    form = RegistrationForm(request.form)

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email'].lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if form.validate():
            db.mysql_cursor.execute("SELECT * FROM Users.User WHERE email = %s", [email])

            if db.mysql_cursor.fetchone() is not None: # The email already exists
                flash("Email already exists")
            elif password != confirm_password:
                flash("The passwords you have entered do not match.")
            else:
                db.mysql_cursor.execute(
                    """INSERT INTO 
                    Users.User (first_name, last_name, password, email)
                    VALUES (%s,%s,%s,%s)""", 
                    (first_name, last_name, generate_password_hash(password), email)
                )
                db.mysql_cnx.commit()

                db.neo4j_driver.session().run("CREATE (u:User {email: $email})", email=email)
                return redirect(url_for("register_api.login"))
        else:
            # form.errors is {field_name_1: [arr, of, errors], ...}
            for errors in form.errors.values():
                for error in errors:
                    flash(error)
    
    return render_template('register.html', form = form)

@register_api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email'].lower()
        password = request.form['password']

        db.mysql_cursor.execute('SELECT password FROM Users.User WHERE email = %s', (email,)) # Tuple with single value needs trailing comma
        result = db.mysql_cursor.fetchone()

        if result and check_password_hash(result[0], password):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            flash("You have entered an invalid email or password.")

    return render_template('login.html')


@register_api.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
