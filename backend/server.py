from flask import Flask

app = Flask(__name__)

# first route
@app.route("/home")
def home():
    return {"packets": ["packet1", "packet2", "packet3"]}

if __name__ == "__main__":
    app.run(debug=True)