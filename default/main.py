import os, datetime, json
from flask import Flask, redirect, request, jsonify, render_template
from google.cloud import storage
from google.cloud import datastore
from google.cloud import vision

import logging 

app = Flask(__name__)


CLOUD_STORAGE_BUCKET = "photo-timeline-shared-new" 

@app.route("/")
def homepage():
    # Lots of logs
    logging.warning("This is a warning")
    logging.debug("Debugging statement")
    logging.error("This is an error")

    datastore_client = datastore.Client.from_service_account_json('photo-timeline-shared-1a2df3229b5e.json')

    query = datastore_client.query(kind='Photos')
    image_entities = list(query.fetch())

    return render_template('homepage.html', image_entities=image_entities)


@app.errorhandler(404)
def page_not_found(e):
    return "Dog not found.", 404

@app.route("/dogs")
def dogs():
  datastore_client = datastore.Client.from_service_account_json('photo-timeline-shared-1a2df3229b5e.json')
  query = datastore_client.query(kind='Photos')
  photo_entities = list(query.fetch())

  json_array=[]
  for entity in photo_entities:
    dict = {}
    dict['blob_name'] = entity['blob_name']
    dict['image_public_url'] = entity['image_public_url']
    dict['timestamp'] = str(entity['timestamp'])
    dict['star_rating'] = entity['star_rating']
    json_array.append(dict)
  return jsonify(json_array), 200


@app.route("/upload", methods=['POST'])
def upload():

  photo = request.files['file']
  star_rating = request.form['star_rating']


  storage_client = storage.Client.from_service_account_json('photo-timeline-shared-new-90ee5b0c603d.json')

  bucket_name = CLOUD_STORAGE_BUCKET
  bucket = storage_client.bucket(bucket_name)

  blob = bucket.blob(photo.filename)
  blob.upload_from_string(photo.read(), content_type=photo.content_type)
  print(f"File uploaded: {photo.filename} to {blob.public_url}")

  client = vision.ImageAnnotatorClient.from_service_account_json('photo-timeline-shared-new-90ee5b0c603d.json')
  image = vision.Image()

  source_uri = 'gs://{}/{}'.format(CLOUD_STORAGE_BUCKET, blob.name)
  image.source.image_uri = source_uri

  response = client.face_detection(image=image)

  print('=' * 30)
  for face in response.face_annotations:
      likelihood = vision.Likelihood(face.surprise_likelihood)
      vertices = ['(%s,%s)' % (v.x, v.y) for v in face.bounding_poly.vertices]
      print('Face surprised:', likelihood.name)
      print('Face bounds:', ",".join(vertices)) 
 

  datastore_client = datastore.Client.from_service_account_json('photo-timeline-shared-new-90ee5b0c603d.json')
  kind = 'Photos'
  name = blob.name
  key = datastore_client.key(kind, name)

  entity = datastore.Entity(key)
  entity['blob_name'] = blob.name
  entity['image_public_url'] = blob.public_url
  entity['timestamp'] = datetime.datetime.now()
  entity['star_rating'] = star_rating if star_rating  else 0

  datastore_client.put(entity)

  return redirect("/", code=200)



if __name__ == '__main__':
  app.run(debug=True)
