import websockets, pathlib, sys, json, pytest

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

class TestClass:
    @pytest.mark.asyncio
    async def test_one(self, start_test_server, test_logger):
            uri = "ws://127.0.0.1:5000/"
            async with websockets.connect(uri, subprotocols=["None"]) as websocket:
                # Enviando mensaje simunlando un ESP32
                mensaje = {
                    "event": "sensor_data",
                    "data": {
                        "valor": 300,
                    },
                }

                await websocket.send(json.dumps(mensaje))

                test_logger.info(f"Test Enviado: {mensaje}")

                # Esperando respuesta
                res = await websocket.recv()

                test_logger.info(f"Respuesta del Server: {res}")

                assert json.loads(res)["status"] == "ok"

    @pytest.mark.asyncio
    async def test_two(self, start_test_server, test_logger):
        uri = "ws://127.0.0.1:5000/dashboard"

        async with websockets.connect(uri, subprotocols=["None"]) as websocket:
            # Esperando la respuesta del Servidor al Front
            res = await websocket.recv()
            # json.loads() Carga un string y lo parsea a un formato JSON (Objeto alias DICT)
            data = json.loads(res)
            assert data["event"] == "historico"
            assert isinstance(data["data"], list)