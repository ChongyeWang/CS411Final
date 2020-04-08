#=========================================
# File name: register.py
# Author: Chongye Wang
# Function: This file handles user system.
#=========================================

from flask import Flask, Blueprint, render_template, flash, request, session, redirect, url_for
from mysql.connector import errorcode
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import check_password_hash, generate_password_hash


register_api = Blueprint('register_api', __name__)

try:
    cnx = mysql.connector.connect(user='admin',
                                  password='adminadmin',
                                  host='database-1.cibdpmq7a2jg.us-east-1.rds.amazonaws.com',
                                  port= 3306)

    cursor = cnx.cursor(buffered=True)

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    else:
        print(err)


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
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

    if form.validate():
        cursor.execute("SELECT * FROM Users.User WHERE email = %s", [email])
        if(cursor.fetchone() is not None): # The email alreay exists
            print(cursor.fetchall())
            print("Fail")
            flash("Email already exists")
        elif(password != confirm_password):
            flash("Password not match")
        else:
            cursor.execute(
                """INSERT INTO 
                Users.User (first_name, last_name, password, email)
                VALUES (%s,%s,%s,%s)""", 
                (first_name, last_name, generate_password_hash(password), email)
            )
            cnx.commit()
            flash('Hello ' + first_name + " " + last_name)
    else:
        flash('All fields are required.')

    return render_template('register.html', form=form)


@register_api.route('/login', methods=['GET', 'POST'])
def login():
    """This function handles user login."""
    msg = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        email = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT password FROM Users.User WHERE email = %s', (email,)) # Tuple with single value needs trailing comma

        result = cursor.fetchone()

        if result:
            if check_password_hash(result[0], password):
                session['email'] = email
                return 'Logged in successfully!'
        else:
            msg = 'Incorrect email or password! Please try again.'
    return render_template('login.html', msg=msg)


@register_api.route('/logout')
def logout():
    """This function handles user logout."""
    session.pop('email', None)
    print(url_for('register_api.login'))
    return redirect(url_for('register_api.login'))
