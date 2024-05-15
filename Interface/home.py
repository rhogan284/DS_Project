from flask import Flask, render_template, request
import os
import json
import mysql.connector

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../Other + Old Scripts/data-systems-assignment-a8059c08d52e.json"

with open('../config.json', 'r') as config_file:
    config = json.load(config_file)

app = Flask(__name__)

db_config = {
    'user': config['db_username'],
    'password': config['db_password'],
    'host': config['jdbc_url'].split('//')[1].split(':')[0],
    'database': config['jdbc_url'].split('/')[-1]
}


@app.route('/')
def index():
    # Establish MySQL connection
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT Flight_ID, Flight_Status, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time
    FROM Flight
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print(data)

    # Close the connection
    cursor.close()
    conn.close()

    return render_template('index.html', data=data)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/user_home', methods=['POST'])
def user_home():
    username = request.form['username']
    return render_template('home.html', username=username)


@app.route('/checkin')
def checkin():
    return render_template('checkin.html')


if __name__ == '__main__':
    app.run(debug=True)
