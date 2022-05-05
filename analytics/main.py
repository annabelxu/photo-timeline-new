from flask import Flask, redirect, request, jsonify, render_template
from google.cloud import storage
from google.cloud import datastore

app = Flask(__name__)

@app.route("/analytics/")
def homepage():
    datastore_client = datastore.Client.from_service_account_json('photo-timeline-shared-new-90ee5b0c603d.json')

    query = datastore_client.query(kind='Photos')
    image_entities = list(query.fetch())

    return render_template('homepage.html', image_entities=image_entities)


if __name__ == '__main__':
  app.run(debug=True)