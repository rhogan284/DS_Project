from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import json
import os

config_path = "../Other + Old Scripts/config.json"
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

db_config = {
    'user': config['db_username'],
    'password': config['db_password'],
    'host': config['jdbc_url'].split('//')[1].split(':')[0],
    'database': config['jdbc_url'].split('/')[-1]
}

app = Flask(__name__)
app.secret_key = 'b14f32e4f9b61e2d4f5e8c43bb2d1a92'

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/refresh')
def refresh():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = f"""
    SELECT DISTINCT Flight_ID, Flight_Status, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time, Aircraft_ID
    FROM {config['flight_table_name']}
    """
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = f"""
        SELECT DISTINCT Flight_ID, Flight_Status, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time,  Aircraft_ID
        FROM {config['flight_table_name']}
        """
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('index.html', username=session['username'], data=data)

@app.route('/aircraft/<aircraft_id>')
def get_aircraft_details(aircraft_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Aircraft WHERE Aircraft_ID = %s"
    cursor.execute(query, (aircraft_id,))
    aircraft = cursor.fetchone()
    cursor.close()
    conn.close()
    if aircraft:
        return jsonify(success=True, **aircraft)
    else:
        return jsonify(success=False)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        # Check if the username already exists
        if any(user['username'] == username for user in users):
            msg = 'Username already exists!'
        else:
            # Add the new user
            users.append({'username': username, 'password': password})
            with open('users.json', 'w') as f:
                json.dump(users, f)
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))

    return render_template('register.html', msg=msg)


@app.route('/checkin')
def checkin():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    return render_template('checkin.html')


@app.route('/checkin/<flight_id>')
def checkin_flight(flight_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = f"""
        SELECT Passport_No, Citizenship, Seat_No
        FROM {config['ticket_table_name']}
        WHERE Flight_ID = %s
        """
    cursor.execute(query, (flight_id,))
    passengers = cursor.fetchall()
    cursor.close()
    conn.close()
    if passengers:
        return jsonify(success=True, passengers=passengers)
    else:
        return jsonify(success=False)

@app.route('/passenger/<passport_number>')
def passenger_details(passport_number):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT First_Name, Last_Name, DOB, Citizenship FROM People WHERE Passport_No = %s"
    cursor.execute(query, (passport_number,))
    passenger = cursor.fetchone()
    cursor.close()
    conn.close()
    if passenger:
        return jsonify(success=True, **passenger)
    else:
        return jsonify(success=False)

@app.route('/stats')
def stats():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('stats.html')


@app.route('/query', methods=['GET', 'POST'])
def query():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    query_result = None
    field_names = None
    if request.method == 'POST':
        query_text = request.form['query']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query_text)
            query_result = cursor.fetchall()
            field_names = [i[0] for i in cursor.description]
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            query_result = f"Error: {err}"

    return render_template('query.html', query_result=query_result, field_names=field_names)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
