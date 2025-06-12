import pathlib, json, asyncio, websockets, datetime

from Logger import Server_Logger
from db import Data_Base

# Doc https://flask.palletsprojects.com/en/latest/quickstart/

LOG_PATH = pathlib.Path(__file__).resolve().parent / "logs"

logger = Server_Logger(logPath=LOG_PATH).get_Logger()

# app = flask.Flask(__file__)

connected_clients = set()
    
data = []

def get_client_by_ip(ip, origin):
    for ws, clientData in connected_clients:
        if clientData[0] == ip and clientData[1] == origin:
            return ws
    
    return None

def get_data_from_db():
    return [{"timestamp": row[0], "valor": row[1]} for row in Data_Base().select_data().fetchall()]

async def handle_client(websocket: websockets.ServerConnection):
    path = websocket.request.path
    cliet_ip = websocket.remote_address[0]
    # if path != "/server" or path != "/page":
    #     logger.warning(f"❌ Path no permitido: {path}")
    #     await websocket.close()
    #     return
    
    logger.info(f"🟢 Cliente conectado path: {path} clint_Ip: {cliet_ip} Subprotocolo aceptado: {websocket.subprotocol}")
    req = websocket.request
    origin = req.headers.get("Origin")
    # print(req.serialize() ,"\n\n", origin)
    connected_clients.add((websocket, (cliet_ip, origin)))

    if path == "/dashboard":
        data = get_data_from_db()
        # print(f"Datos db: {data}")
        await websocket.send(json.dumps({
            "event": "historico",
            "data": data
        }))


    try:
        async for message in websocket:
            logger.info(f"📩 Mensaje recibido: {message}")

            try:
                data = json.loads(message)

                if data.get("event") == "sensor_data":

                    valor = data["data"]["valor"]
                    # logger.info(f"📈 Valor del sensor: {valor}")
                    local_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    Data_Base().insert_data(valor, local_timestamp)

                    await websocket.send(json.dumps({"status": "ok", "mensaje": "Dato recibido"}))

                    front = get_client_by_ip("127.0.0.1", "http://localhost:4321")
                    if front:
                        logger.info(f"📡 Comunicandose con el Front")
                        await front.send(json.dumps({
                            "event": "sensor_data",
                            "data": json.dumps({"timestamp": local_timestamp, "valor": valor})
                        }))

                else:
                    await websocket.send(json.dumps({"status": "error", "mensaje": "Evento desconocido"}))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"status": "error", "mensaje": "JSON inválido"}))
                
    except websockets.ConnectionClosed:
        logger.info("🔌 Cliente desconectado")

    finally:
        connected_clients.remove((websocket, (websocket.remote_address[0], websocket.request.headers.get("Origin"))))

async def start_server():

    logger.info("🟢 Iniciando servidor WebSocket en ws://127.0.0.1:5000")

    async with websockets.serve(handle_client, "0.0.0.0", 5000, subprotocols=["None","arduino"], ping_timeout=60):
        await asyncio.Future()  # Mantener servidor activo

if __name__ == "__main__":
    asyncio.run(start_server())

# @app.route("/", methods=['GET'])
# def hello_Json():
#     req = flask.request
#     logger.info(f"Entro al servidor HTTP Host:{req.host}, Method:{req.method}")
#     return {
#         "Mensaje": "Hola Sapa",
#         "Host": req.host,
#         "Method": req.method,
#         "CurrentData": data
#     }

# @socket.route("/ws")
# def websocket_route(ws):
#     while True:
#         try:
#             raw = ws.receive()
#             if not raw:
#                 break

#             logger.info(f"📩 Recibido: {raw}")
#             data = json.loads(raw)
#             event = data.get("event")
#             if event == "sensor_data":
#                 valor = data["data"]["valor"]
#                 logger.info(f"🧪 Valor del sensor: {valor}")

#                 # Enviar ACK
#                 logger.info(f"Enviando un ACK al CLiente!")
#                 ws.send(json.dumps({"event": "ACK"}))
#         except Exception as e:
#             logger.exception(msg="Error", exc_info=e)

# @socket.on('connect')
# def test_connect():
#     print('Cliente conectado:', flask.request.sid)

# @socket.on('disconnect')
# def test_disconnect():
#     print('Cliente desconectado:', flask.request.sid)

# @socket.route("/sensor_data")
# def handler_sensor_data(ws):
#     print(ws.receive())
#     logger.info(f"Dato recibido del ESP32: {ws.receive()}")

# if __name__ == "__main__":
#     logger.info("Servidor establecido en http://192.168.20.173 puerto 5000 y http://127.0.0.1:5000")
#     socket.run(app, host="0.0.0.0", port=5000)