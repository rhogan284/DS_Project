from flask import Flask, render_template, request, jsonify
import mysql.connector
import json

# Load configuration from the JSON file
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

@app.route('/')
def index():
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

    return render_template('index.html', data=data)

@app.route('/refresh')
def refresh():
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
