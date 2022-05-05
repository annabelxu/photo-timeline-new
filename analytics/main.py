from flask import Flask, redirect, request, jsonify, render_template

app = Flask(__name__)

@app.route("/analytics/")
def homepage():
  return "hello from analytics", 200
    

if __name__ == '__main__':
  app.run(debug=True)