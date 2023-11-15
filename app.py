from flask import Flask, render_template, request, make_response, redirect, url_for
import sqlite3

import hashlib

app = Flask(__name__)


@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html', error = None)


@app.route('/login', methods=['GET', 'POST'])
def check_credentials():
    error = None
    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']
        
        with sqlite3.connect("db.sqlite3") as connection:

            cursor = connection.cursor()

            cursor.execute("SELECT * FROM Credentials WHERE Username = ? AND Password = ?", (input_username, hash_password(input_password)))
    
            result = cursor.fetchone()
            
        if result:
            # Simulate a successful login
            user = result
            # Store user information in a cookie
            response = make_response(render_template('login_success.html', user=user))

            response.set_cookie('ID', str(user[0]))
            response.set_cookie('Username', str(user[1]))

            return response
        else:
            # Simulate an incorrect login
            return render_template('sign_up.html')


# Function hash ALL PASSWORDS in database
def salt_passwords():
    with sqlite3.connect("db.sqlite3") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT Username, Password FROM Credentials")
        result = cursor.fetchall()

        for user in result:
            salted_password = hash_password(user[1])
            cursor.execute("UPDATE Credentials SET Password = ? WHERE Username = ?", (salted_password, user[0]))


# Function to get the result of hashing a password
def hash_password(password):
    # Encode for hashing to work
    password = password.encode('utf-8')

    hash = hashlib.sha256()         # Create Hashing object
    hash.update(password)           # Apply hashing algorithm
    hash_pass = hash.hexdigest()    # Use hex representation

    return hash_pass

        
@app.route('/sign_up', methods=['POST'])
def sign_up():
    new_username = request.form['username']
    new_password = request.form['password']

    first_name = request.form['firstname']
    last_name = request.form['lastname']

    with sqlite3.connect("db.sqlite3") as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Credentials WHERE Username = ? AND Password = ?", (new_username, hash_password(new_password)))

        result = cursor.fetchone()

        if result:
            # Simulate a successful login
            user = result
            # Store user information in a cookie
            response = make_response(render_template('login_success.html', user=user))

            response.set_cookie('ID', str(user[0]))
            response.set_cookie('Username', str(user[1]))
            
            return render_template('login_success.html', user=result)
        else:
            # Input new user into database
            cursor.execute("SELECT MAX(ID) FROM Credentials")
            new_ID = cursor.fetchone()[0] + 1
            
            cursor.execute("INSERT INTO Credentials (ID, Username, Password) VALUES (?, ?, ?)", (new_ID, new_username, hash_password(new_password)))
            cursor.execute("INSERT INTO PatientInformation (ID, First_Name, Last_Name) VALUES (?, ?, ?)", (new_ID, first_name, last_name))
        
            return render_template('login_success.html', user=result)


@app.route('/patient_info', methods=['GET', 'POST'])
def display_info():
    # Check if 'ID' and 'Username' cookies are present
    if 'ID' in request.cookies and 'Username' in request.cookies:
        user_id = request.cookies.get('ID')
        username = request.cookies.get('Username')

        with sqlite3.connect("db.sqlite3") as connection:
            cursor = connection.cursor()

            # Check if the user is an admin (you might have a column like 'IsAdmin' in your Credentials table)
            cursor.execute("SELECT * FROM Credentials WHERE ID = ?", (user_id,))
            user = cursor.fetchone()

            if user and user[3]:
                # User is an admin, display all users
                all_users = cursor.execute("SELECT * FROM PatientInformation").fetchall()
                return render_template('patient_info.html', users = all_users)
            else:
                # User is not an admin, display single user
                user_data = cursor.execute("SELECT * FROM PatientInformation WHERE ID = ?", (user_id,)).fetchone()
                return render_template('patient_info.html', user = user_data)
    else:
        # If cookies are not present, redirect to login page or handle the situation accordingly
        return redirect('/login')


def remove_user(id):
    with sqlite3.connect("db.sqlite3") as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Credentials WHERE ID = ?", (id,))


def home():
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear the cookies by creating a response and deleting the cookies
    response = make_response(redirect(url_for('login_page')))  # Redirect to login page
    response.set_cookie('ID', '', expires = 0)  # Clear 'ID' cookie
    response.set_cookie('Username', '', expires = 0)  # Clear 'Username' cookie
    return response


if __name__ == '__main__':
    app.run()