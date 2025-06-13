import asyncio, websockets, pathlib, sys, json, pytest, os, subprocess, time

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

from src.Logger import Server_Logger

@pytest.fixture(scope="module")
def start_test_server(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data") / "test_data.db"

    env = os.environ.copy()
    env["DB_PATH"] = str(db_path)

    proc = subprocess.Popen(
        ["C:/Users/sebax/Desktop/Universidad/Proyectos_aleatorios/WebSocket Con Flask/.UVEnv/Scripts/python.exe", str(BASE_DIR / "src" / "server.py"), "--host", "127.0.0.1", "--port", "5000"],
        env=env,
    )

    # Esperando a que el servidor arranque
    time.sleep(5)

    # Mandando el path al test
    yield db_path

    proc.terminate()
    proc.wait()

class TestClass:
    @pytest.mark.asyncio
    async def test_one(self, start_test_server):
            logger = Server_Logger(BASE_DIR / "Test").get_Logger()
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

                logger.info(f"Test Enviado: {mensaje}")

                # Esperando respuesta
                res = await websocket.recv()

                logger.info(f"Respuesta del Server: {res}")

                assert json.loads(res)["status"] == "ok"