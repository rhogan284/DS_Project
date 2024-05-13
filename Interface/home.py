from flask import Flask, render_template, request
from google.cloud import bigquery



app = Flask(__name__)

# client = bigquery.Client()


@app.route('/')
def index():

    # query = """
    #     SELECT * FROM 'insert table name here'
    # """
    # query_job = client.query(query)
    # results = query_job.result()

    return(render_template('index.html'))

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