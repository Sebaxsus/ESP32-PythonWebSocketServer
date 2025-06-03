import flask

# Doc https://flask.palletsprojects.com/en/latest/quickstart/

app = flask.Flask(__file__)

@app.route("/", methods=['GET'])
def hello_Json():
    req = flask.request
    return {
        "Mensaje": "Hola Sapa",
        "Host": req.host,
        "Method": req.method
    }