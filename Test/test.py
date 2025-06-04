import asyncio, websockets, json, pathlib, sys, os

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

from src.Logger import Server_Logger

async def test_client():
    uri = "ws://127.0.0.1:5000/"
    logger  = Server_Logger(BASE_DIR / "Test").get_Logger()
    try:
        async with websockets.connect(uri, subprotocols=["None"]) as websocket:
            # Enviando mensaje simunlando un ESP32
            mensaje = {
                "event": "sensor_data",
                "data": {
                    "valor": 400,
                },
            }

            await websocket.send(json.dumps(mensaje))

            logger.info(f"Test Enviado: {mensaje}")

            # Esperando respuesta
            res = await websocket.recv()

            logger.info(f"Respuesta del Server: {res}")
    except Exception as e:
        logger.error(f"❌ Error al conectar o enviar datos: {e}")

async def test_client_db():
    uri = "ws://127.0.0.1:5000/dashboard"
    logger  = Server_Logger(BASE_DIR / "Test").get_Logger()
    try:
        async with websockets.connect(uri, subprotocols=["None"]) as websocket:

            # Esperando respuesta
            res = await websocket.recv()

            logger.info(f"Respuesta del Server: {res}")
    except Exception as e:
        logger.error(f"❌ Error al conectar o enviar datos: {e}")

asyncio.run(test_client())
asyncio.run(test_client_db())