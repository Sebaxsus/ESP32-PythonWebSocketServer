import flask, pathlib, json
from flask_sock import Sock
from Logger import Server_Logger

# Doc https://flask.palletsprojects.com/en/latest/quickstart/

LOG_PATH = pathlib.Path(__file__).resolve().parent / "logs"

logger = Server_Logger(logPath=LOG_PATH).get_Logger()

app = flask.Flask(__file__)
socket = Sock(app, cors_allowed_origins="*", engineio_logger=True, logger=True, ping_interval=25 , ping_timeout=60)

data = []

@app.route("/", methods=['GET'])
def hello_Json():
    req = flask.request
    logger.info(f"Entro al servidor HTTP Host:{req.host}, Method:{req.method}")
    return {
        "Mensaje": "Hola Sapa",
        "Host": req.host,
        "Method": req.method,
        "CurrentData": data
    }

@socket.route("/ws")
def websocket_route(ws):
    while True:
        raw = ws.receive()
        event, data = json.load(raw)
        if event == "sensor_data":
            print("Dato recibido del ESP32:", data)
        print(f"No entro a event: {event}, data: {data}")
        ws.send("ACK")

# @socket.on('connect')
# def test_connect():
#     print('Cliente conectado:', flask.request.sid)

# @socket.on('disconnect')
# def test_disconnect():
#     print('Cliente desconectado:', flask.request.sid)

@socket.route("/sensor_data")
def handler_sensor_data(ws):
    print(ws.receive())
    logger.info(f"Dato recibido del ESP32: {ws.receive()}")

if __name__ == "__main__":
    logger.info("Servidor establecido en el puerto 5000")
    socket.run(app, host="0.0.0.0", port=5000)