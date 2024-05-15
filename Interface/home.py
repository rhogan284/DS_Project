from flask import Flask, render_template, request, jsonify
import mysql.connector
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

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


@app.route('/checkin/<flight_id>', methods=['GET'])
def get_passenger_list(flight_id):
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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = f"""
    SELECT Flight_Status, COUNT(*) as count
    FROM {config['flight_table_name']}
    GROUP BY Flight_Status
    """
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(data, columns=['Flight_Status', 'Count'])

    # Plot the data
    fig, ax = plt.subplots()
    sns.barplot(x='Flight_Status', y='Count', data=df, ax=ax)
    plt.title('Flight Status Distribution')

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return render_template('stats.html', image_base64=image_base64)


if __name__ == '__main__':
    app.run(debug=True)
