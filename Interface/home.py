from flask import Flask, render_template, request
from google.cloud import bigquery
import os 

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../Other + Old Scripts/data-systems-assignment-a8059c08d52e.json"

client = bigquery.Client()


app = Flask(__name__)


@app.route('/')
def index():

    query = """ SELECT DISTINCT Flight_ID, Flight_Status, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time
 FROM `data-systems-assignment.Airport_Dataset.Flights_Table_Test` 
"""
    query_job = client.query(query)
    return(render_template('index.html', data=query_job.result()))

@app.route('/login')
def login():
    return(render_template('login.html'))


@app.route('/user_home', methods=['POST'])
def user_home():
    username = request.form['username']
    return(render_template('home.html', username=username))

@app.route('/checkin')
def checkin():
    return(render_template('checkin.html'))


if __name__ == '__main__':
    app.run(debug=True)