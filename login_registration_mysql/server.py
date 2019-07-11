from flask import Flask, render_template, request, redirect, session, flash
import re
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
app = Flask(__name__)
app.secret_key = "it's a secret"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=.*?[0-9]).{8,}$')
is_valid_name = re.compile(r'[a-zA-Z]+')
# *****************HOMEPAGE FOR LOGGING IN***************************
@app.route('/')
def loginPage():
    pass
    return render_template('index.html')

# ***************THE SUCCESS PAGE IF REGISTRATION GOES THROUGH*******************
@app.route('/success')
def loginSuccess():
    if 'id' not in session:
        flash("You must be logged in!", "red")
        return redirect ('/')
    return render_template('success.html')

# ********************* WHEN A NEW REGISTRATION IS SUBMITTED **************************
@app.route('/user/review', methods=['POST'])
def registrationAuthentification():
    mysql=connectToMySQL('loginregistration')
    query = "SELECT * FROM users;"
    user = mysql.query_db(query)
    is_valid = True
#First Name Validations *******************************
    if len(request.form['first_name']) == 0:
        is_valid = False
        flash("please submit your first name!", "red")
    if not is_valid_name.match(request.form['first_name']):
        is_valid = False
        flash("please submit your first name, not numbers!", "red")
    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("please enter over 2 characters", "red")
#Last Name Validations *******************************
    if len(request.form['last_name']) == 0:
        is_valid = False
        flash("please submit your last name!", "red")
    if not is_valid_name.match(request.form['last_name']):
        is_valid = False
        flash("please submit your last name, not numbers!", "red")
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("please enter over 2 characters", "red")
#Email Validations *******************************
    if len(request.form['email']) == 0:
        is_valid = False
        flash("please submit your email!", "red")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("invalid email address!", "red")
        return redirect('/')
    for user in user:
        if request.form['email'] == user['email']:
            is_valid = False
            flash("email address already exists!", "red")
            return redirect('/')
#Password Validations *******************************
    if not PASSWORD_REGEX.match(request.form['password']):
        is_valid = False
        flash('Please enter a password with 8 or more characters with at least one capitalized letter & one number', "red")
    # if len(request.form['password']) < 8:
    #     is_valid = False
    #     flash('Please enter a password with 8 or more characters', "red")
    if not request.form['password_confirm'] == request.form['password']:
        is_valid = False
        flash('Passwords must match', "red")
    if not is_valid:
        return redirect('/')
    else:
        flash("you've been successfully registered!", "green")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        mysql = connectToMySQL("loginregistration")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(psw)s, NOW(), NOW());"
        data = {
            "fn": request.form['first_name'],
            "ln": request.form['last_name'],
            "em": request.form['email'],
            "psw": pw_hash
        } 
        print(user)
        new_user = mysql.query_db(query, data)
        session['id'] = new_user
        print(session)
        return redirect('/success')

# ********************WHEN A PREVIOUS USER LOGS IN************************
@app.route('/user/login', methods = ['POST'])
def loginAuthentification():
    mysql = connectToMySQL("loginregistration")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data =  {
        "email": request.form['email']
    }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['id'] = result[0]['id']
            print(session)
            flash("you logged in successfully!", "green")
            return redirect ('/success')
    flash("You could not be logged in", "red")
    return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    print(session)
    return redirect ('/')


if __name__ == '__main__':
    app.run(debug=True)
