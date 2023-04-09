from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../bot/data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'app'
db = SQLAlchemy(app)



class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    telegram_name = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(14), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User('{self.name}', {self.telegram_name} '{self.login}', '{self.age}')"

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return redirect('https://t.me/Roman_Test_Registraion_bot', code=302)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        # Get username and password from the form
        login = form.login.data
        password = form.password.data
        # Check if a user with this name and password exists in the database
        user = Users.query.filter_by(login=login, password=password).first()
        if user:
            return redirect(url_for('account', login=login))
        else:
            flash('Invalid login or password', 'danger')
    return render_template('signin.html', form=form)

@app.route('/account/<login>')
def account(login):
    # Retrieving user data from the database
    user = Users.query.filter_by(login=login).first()

    return render_template('account.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
