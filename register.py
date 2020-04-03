from flask import Flask, render_template, flash, request
from mysql.connector import errorcode
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

from flask import Blueprint

register_api = Blueprint('register_api', __name__)


app = Flask(__name__)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

visit_counter_home = 1


class RegistrationForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required()])
    confirm_password = TextField('Confirm Password:', validators=[validators.required()])
    

@register_api.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    print (form.errors)
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['name']
        password=request.form['name']
        cofirm_password=request.form['name']
        print(name)
        print(email)
        print(password)
        print(confirm_password)

    if form.validate():
        flash('Hello ' + name)
    else:
        flash('All the form fields are required. ')

    return render_template('register.html', form=form)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
