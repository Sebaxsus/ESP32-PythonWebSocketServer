import pathlib, json, asyncio, websockets, datetime, os, urllib
import urllib.parse

from Logger import Server_Logger
from db import Data_Base

# Doc https://flask.palletsprojects.com/en/latest/quickstart/

LOG_PATH = pathlib.Path(__file__).resolve().parent / "logs"

DEFUALT_DB_PATH = pathlib.Path(__file__).resolve().parent / "data.db"

logger = Server_Logger(logPath=LOG_PATH).get_Logger()

# app = flask.Flask(__file__)

connected_clients = set()
    
data = []

def get_query_data(QueryObject: dict) -> list[tuple[str|None, str|None] | tuple[None, None]]:
    """
    Como el orden va a ser complicado mi acercamiento a la solucion es 
    Guardar en valor un `STRING` concatenado que lo separe un `|` y que contenga
    el valor en el cual se basará el ordenamiento es decir `timestamp ASC` Ó `valor DESC`
    """
    # Manejando el caso en el que no se mande el Parametro de Ruta `order`
    if QueryObject.get("order") == None:
        return (None, None)
        # Todavia no manejo errores, Esto seria un Error, Pero Tambien seria el caso en el que no se usen fitlros
        # 😡
    QueryData = []
    for key in QueryObject.keys():
        if key in ["date", "value"]:
            QueryData.append( ( key, f"{QueryObject.get(key)[0]}|{QueryObject.get("order")[0]}" ) )
    # Como todavia no esta implementado el filtro por Fecha y Valor entonces me salto esto
    # Y solo utilizo la unica tupla que se recive
    return QueryData[0] if len(QueryData) > 0 else (None, None)

def get_client_by_ip(ip, origin):
    for ws, clientData in connected_clients:
        if clientData[0] == ip and clientData[1] == origin:
            return ws
    
    return None

def get_data_from_db(db_path: pathlib.Path, type: str|None, value: str|None) -> list[dict["timestap": str,"valor": str]]:
    if value:
        desestructurando_la_Query = value.split("|") # Separo el String "2025-04-12|timestamp ASC"
    else:
        desestructurando_la_Query = [None, None]
    logger.debug(f"Query desestructurada: {desestructurando_la_Query}, type: {type}")
    with Data_Base(logger, db_path) as db:
        if type == "date" and value:
            temp = [{"timestamp": row[0], "valor": row[1]} for row in db.filter_by_date(desestructurando_la_Query[0], desestructurando_la_Query[1])]
            logger.debug(f"Respuesta dentro de Func {temp}")
            return temp
        elif type == "value" and value:
            temp = [{"timestamp": row[0], "valor": row[1]} for row in db.filter_by_value(desestructurando_la_Query[0], desestructurando_la_Query[1])]
            logger.debug(f"Respuesta dentro de Func {temp}")
            return temp
        else:
            return [{"timestamp": row[0], "valor": row[1]} for row in db.select_data(desestructurando_la_Query[1])]

async def handle_client(websocket: websockets.ServerConnection):
    path = websocket.request.path
    cliet_ip = websocket.remote_address[0]
    # if path != "/server" or path != "/page":
    #     logger.warning(f"❌ Path no permitido: {path}")
    #     await websocket.close()
    #     return
    subprotocol = websocket.subprotocol
    logger.info(f"🟢 Cliente conectado path: {path} clint_Ip: {cliet_ip} Subprotocolo aceptado: {subprotocol}")
    req = websocket.request
    origin = req.headers.get("Origin")
    # print(req.serialize() ,"\n\n", origin)
    connected_clients.add((websocket, (cliet_ip, origin)))
    db_path = pathlib.Path(os.getenv("DB_PATH", DEFUALT_DB_PATH))

    if "/dashboard" in path:
        # Parseando la URL con URLLIB para separar el "EndPoint" del "QueryString o QueryParameters
        # Url Ejemplo: ws:127.0.0.1/dashboard?date=2025-03-12
        parsedPath = urllib.parse.urlparse(path)
        # route = parsedPath.path # "/dashboard"
        query = urllib.parse.parse_qs(parsedPath.query) # {"date": ["2025-03-12"]}
        # logger.info(f"QueryParams: {query}\n Keys: {query.keys()}\n Date: {query.get("date")}\n Value: {query.get("value")}")
        # if query.get("date"):
        #     queryType = "date"
        #     queryValue = query.get("date")[0]
        # elif query.get("value"):
        #     queryType = "value"
        #     queryValue = query.get("value")[0]
        # else:
        #     queryType = None
        #     queryValue = None

        queryData = get_query_data(query)

        logger.info(f"QueryParams Parseado: {queryData}")

        data = get_data_from_db(db_path, queryData[0], queryData[1])
        logger.debug(f"Respuesta de la BD: {data}")
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

                    with Data_Base(logger, db_path) as db:
                        # Hardcodeado para que Genere la tabla en caso
                        # De que la peticion sea del Test (Subprotocolo None)
                        # Es una mala practica pero funciona
                        # \_(シ)_/ 🤷‍♂️
                        if subprotocol == "None":
                            db.init_db()
                        db.insert_data(valor, local_timestamp)

                    await websocket.send(json.dumps({"status": "ok", "mensaje": "Dato recibido"}))

                    front = get_client_by_ip("127.0.0.1", "http://localhost:4321")
                    if front:
                        logger.info(f"📡 Comunicandose con el Front")
                        await front.send(json.dumps({
                            "event": "sensor_data",
                            "data": json.dumps({"timestamp": local_timestamp, "valor": valor})
                        }))
                elif data.get("event") == "historico":
                    dbData = None
                    filter_data = data.get("filter")
                    order = data.get("order")
                    logger.debug(f"Datos dentro de la peticion {filter_data}, {order}, {data}")
                    # Esta condición no tiene sentido ya que dentro de la funcion `get_data_from_db` ya manejo el caso de que los dos sean None o que Solo alguno de los dos sea None
                    if not filter_data and not order:
                        # Si llega aqui significa que no se especifico un orden o filtrar por algo en especifico
                        # Por ende repondo como si fuera una query default (Todos los datos filtrando por los 100 mas recientes usando de base el timestamp)
                        dbData = get_data_from_db(db_path, None, None)
                        await websocket.send(json.dumps({
                            "event": "historico",
                            "data": dbData
                        }))
                    else:
                        # Debo parsear la entrada a un string como esepra la funcion
                        # en filter_data debe almacenar un Objeto (Dict) el cual su llave es el tipo de columna y el valor el filtro
                        # en Order viene un Objeto (Dict) con dos atributos (order, by) en donde order sera (ASC o DESC) y BY la Columna (Column valor|timestamp)
                        
                        # Validando que el Objeto order venga bien estructurado
                        orderString = None
                        filter_Type = None
                        if order.get("by") and order.get("direction"):
                            orderString = f"{order.get("by")} {order.get("direction")}"
                        # else:
                        #     orderString = None
                        
                        # Toca cambiar como se comporta la funcion get_data_from_db ya que debe tener otro tipo
                        # Para poder manejar cuando se usa un Filtro especifico
                        # filter_data[0][0] # Item 0 AKA Objeto 1 (Clave, Valor), Index [0] AKA Calve
                        # filter_data[0][1] # Item 0 AKA Objeto 1 (Clave, valor), Index [1] AKA Valor
                        # orderString = f"WHERE {filter_data[0][0]} <= {filter_data[0][1]} ORDER BY {orderString}"
                        # Re-usando la logica anterior filter_value|column direction
                        if filter_data:
                            for key,value in  filter_data.items():
                                logger.debug(f"Objeto filter_data: {key},{value}")
                                orderString = f"{value}|{orderString}"
                                if key == "date":
                                    filter_Type = "date"
                                else:
                                    filter_Type = "value"
                        else:
                            orderString = f"{datetime.datetime.now().strftime("%Y-%m-%d")}|{orderString}"
                            filter_Type = "date"
                        dbData = get_data_from_db(db_path, filter_Type, orderString)
                        logger.debug(f"Respuesta de la BD: {dbData}")
                        await websocket.send(json.dumps({
                            "event": "historico",
                            "data": dbData
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