from flask import Flask, jsonify
from flask_cors import CORS
from database.query_apis import get_flow_table, get_frame_table, get_volume_data, get_packet_types, get_top_domains

app = Flask(__name__)
CORS(app) # needed so that flask and react can communicate

# first route
@app.route("/flowsTable")
def flowsTable():
    flow_data = get_flow_table()
    return jsonify(flow_data) # return list of dicts as json using flask.jsonify

@app.route("/framesTable")
def framesTable():
    frame_data = get_frame_table()
    return jsonify(frame_data)

@app.route("/volumeData")
def volumeData():
    volume_data = get_volume_data()
    return jsonify(volume_data)

@app.route("/packetTypes")
def packetTypes():
    packet_types = get_packet_types()
    return jsonify(packet_types)

@app.route("/topDomains")
def topDomains():
    top_domains = get_top_domains()
    return jsonify(top_domains)

if __name__ == "__main__":
    app.run(debug=True)