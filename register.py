#=========================================
# File name: register.py
# Author: Chongye Wang
# Function: This file handles user system.
#=========================================

from flask import Flask, Blueprint, render_template, flash, request, session, redirect, url_for
from mysql.connector import errorcode
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash
import db

register_api = Blueprint('register_api', __name__)

class RegistrationForm(Form):
    first_name = TextField('First Name:', validators=[validators.required()])
    last_name = TextField('Last Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required()])
    confirm_password = TextField('Confirm Password:', validators=[validators.required()])
    

@register_api.route('/register', methods=['GET', 'POST'])
def register():
    """This function handles user registration."""
    form = RegistrationForm(request.form)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email'].lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

    if form.validate():
        db.mysql_cursor.execute("SELECT * FROM Users.User WHERE email = %s", [email])
        if(db.mysql_cursor.fetchone() is not None): # The email alreay exists
            flash("Email already exists")
        elif(password != confirm_password):
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
            flash('Hello ' + first_name + " " + last_name)
    else:
        flash('All fields are required.')

    return render_template('register.html', form=form)


@register_api.route('/login', methods=['GET', 'POST'])
def login():
    """This function handles user login."""
    msg = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        email = request.form['username'].lower()
        password = request.form['password']
        db.mysql_cursor.execute('SELECT password FROM Users.User WHERE email = %s', (email,)) # Tuple with single value needs trailing comma

        result = db.mysql_cursor.fetchone()

        if result:
            if check_password_hash(result[0], password): # Successfully logged in
                session['email'] = email
                return redirect(url_for('index'))
        else:
            msg = 'Incorrect email or password! Please try again.'
    return render_template('login.html', msg=msg)


@register_api.route('/logout')
def logout():
    """This function handles user logout."""
    session.clear()
    return redirect(url_for('index'))
