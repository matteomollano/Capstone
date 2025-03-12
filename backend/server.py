from flask import Flask, jsonify
from flask_cors import CORS
from database.query_apis import get_flow_table

app = Flask(__name__)
CORS(app) # needed so that flask and react can communicate

# first route
@app.route("/home")
def home():
    flow_data = get_flow_table()
    return jsonify(flow_data) # return list of dicts as json using flask.jsonify

if __name__ == "__main__":
    app.run(debug=True)