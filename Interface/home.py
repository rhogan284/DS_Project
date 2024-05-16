from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os

# Load configuration from the config file
config_path = "../config.json"
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
    SELECT DISTINCT Flight_ID, Flight_Status, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time
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
        SELECT DISTINCT Flight_ID, Flight_Status, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time
        FROM {config['flight_table_name']}
        """
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('index.html', username=session['username'], data=data)


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


@app.route('/checkin/<flight_id>', methods=['GET'])
def get_passenger_list(flight_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

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
        passenger_list = [
            {"passportNumber": p[0], "citizenship": p[1], "seatNumber": p[2]}
            for p in passengers]
        return jsonify(success=True, passengers=passenger_list)
    else:
        return jsonify(success=False)

@app.route('/stats')
def stats():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch flight status distribution
    query = f"""
    SELECT Flight_Status, COUNT(*) as count
    FROM {config['flight_table_name']}
    GROUP BY Flight_Status
    """
    cursor.execute(query)
    status_data = cursor.fetchall()

    # Fetch data for arrivals and departures per hour
    query = f"""
        SELECT HOUR(Departure_Time) as Hour, COUNT(*) as Count, 'Departure' as Type
        FROM {config['flight_table_name']}
        GROUP BY HOUR(Departure_Time)
        UNION
        SELECT HOUR(Arrival_Time) as Hour, COUNT(*) as Count, 'Arrival' as Type
        FROM {config['flight_table_name']}
        GROUP BY HOUR(Arrival_Time)
        """
    cursor.execute(query)
    hourly_data = cursor.fetchall()

    # Fetch passengers per flight
    query = f"""
        SELECT Flight_ID, COUNT(*) as Count
        FROM {config['ticket_table_name']}
        GROUP BY Flight_ID
        """
    cursor.execute(query)
    passengers_per_flight = cursor.fetchall()

    # Fetch citizenship distribution (top 10)
    query = f"""
     SELECT Citizenship, COUNT(*) as Count
     FROM {config['ticket_table_name']}
     GROUP BY Citizenship
     ORDER BY Count DESC
     LIMIT 10
     """
    cursor.execute(query)
    citizenship_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Create DataFrames from the fetched data
    status_df = pd.DataFrame(status_data, columns=['Flight_Status', 'Count'])
    hourly_df = pd.DataFrame(hourly_data, columns=['Hour', 'Count', 'Type'])
    passengers_df = pd.DataFrame(passengers_per_flight, columns=['Flight_ID', 'Count'])
    citizenship_df = pd.DataFrame(citizenship_data, columns=['Citizenship', 'Count'])

    # Plot the flight status distribution
    fig1, ax1 = plt.subplots()
    sns.barplot(x='Flight_Status', y='Count', data=status_df, ax=ax1)
    plt.title('Flight Status Distribution')
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    image_base64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    buf1.close()

    # Plot arrivals and departures per hour
    fig2, ax2 = plt.subplots()
    sns.lineplot(x='Hour', y='Count', hue='Type', data=hourly_df, ax=ax2)
    plt.title('Arrivals and Departures per Hour')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Flights')
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    image_base64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    buf2.close()

    # Plot passengers per flight
    fig3, ax3 = plt.subplots()
    sns.barplot(x='Flight_ID', y='Count', data=passengers_df, ax=ax3)
    plt.title('Passengers per Flight')
    plt.xlabel('Flight ID')
    plt.ylabel('Number of Passengers')
    plt.xticks(rotation=90, ha='right', fontsize=8)
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png', bbox_inches='tight')
    buf3.seek(0)
    image_base64_3 = base64.b64encode(buf3.getvalue()).decode('utf-8')
    buf3.close()

    # Plot top 10 passenger citizenships
    fig4, ax4 = plt.subplots()
    sns.barplot(x='Citizenship', y='Count', data=citizenship_df, ax=ax4)
    plt.title('Top 10 Passenger Citizenship Distribution')
    plt.xlabel('Citizenship')
    plt.ylabel('Number of Passengers')
    plt.xticks(rotation=90, ha='right', fontsize=8)
    buf4 = io.BytesIO()
    plt.savefig(buf4, format='png', bbox_inches='tight')
    buf4.seek(0)
    image_base64_4 = base64.b64encode(buf4.getvalue()).decode('utf-8')
    buf4.close()

    return render_template('stats.html',
                           image_base64_1=image_base64_1,
                           image_base64_2=image_base64_2,
                           image_base64_3=image_base64_3,
                           image_base64_4=image_base64_4)


if __name__ == '__main__':
    app.run(debug=True)
