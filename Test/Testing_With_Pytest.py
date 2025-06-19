import websockets, pathlib, sys, json, pytest

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

class TestClass:
    """
    Al declarar una clase dentro con el prefijo (Prefix) reservado por Pytest
    `Test` Pytest la entiende y todos sus metodos tambien deben iniciar con el prefijo
    (Prefix) test_ para que pytest lo entienda y lo ejecute,

    En resumen Pytest reserva el prefijo `Test y test_` para ejecutar varios test y organizarlos dentro
    de una clase.

    ---

    Para usar los fixture de `conftest.py` solo toca llamar el nombre de el metodo declarado
    en `conftest.py`

    ---

    Como los test son asincronos toca instalar el plug-in de pytest `pytest-asyncio`
    y usar el decorador `@pytest.mark.asyncio`

    ---

    Al iniciar el Test el Fixture `start_test_server` se encarga de iniciar el servidor WebSocket y Definir una ruta
    **TEMPORAL** para la base de datos con el fin de no afectar los datos Almacenados dentro de la Base De Datos
    """
    @pytest.mark.asyncio
    async def test_one(self, start_test_server, test_logger):
            """
            Este test se encarga de simular una interaccion entre el ESP32
            y el WebSocket, Conectandose al WebSocket y luego mandando un dato de prueba.
            """
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
        """
        Este test se encarga de simular una interaccion entre la Pagina Web y el Servidor WebSokcet,
        Conectandose al Servidor con el Path (Ruta) `/dashboard`

        **SENDS:**
            `Connection with path "/dashboard"`

        **EXPECTS:**
            `(Objet with attribute "event") with a value "historico"`
            `(Object with attribute "data") with a data Type (list)`
        """
        uri = "ws://127.0.0.1:5000/dashboard"

        async with websockets.connect(uri, subprotocols=["None"]) as websocket:
            test_logger.info(f"Test Endpoint: '/dashboard'")

            # Esperando la respuesta del Servidor al Front
            res = await websocket.recv()

            # json.loads() Carga un string y lo parsea a un formato JSON (Objeto alias DICT)
            data = json.loads(res)

            test_logger.info(f"Respuesta del Server: {res}")

            assert data["event"] == "historico"
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_three(self, start_test_server, test_logger):
        """
        Este test se encarga de simular una interaccion entre la Pagina Web y el Servidor WebSokcet,
        Conectandose al Servidor con el Path (Ruta) `/dashboard` y el Parametro de Ruta (QueryParam) `date`

        **SENDS:**
            `Connection with path "/dashboard?date=YYYY-MM-DD&order=timestamp%20DESC"`

        **EXPECTS:**
            `(Objet with attribute "event") with a value "historico"`
            `(Object with attribute "data") with a data Type (list)`
        """
        uri = "ws://127.0.0.1:5000/dashboard?date=2025-03-12&order=timestamp%20DESC"

        async with websockets.connect(uri, subprotocols=["None"]) as websocket:
            test_logger.info(f"Test Endpoint + QueryParam: '/dashboard?date=2025-03-12&order=timestamp%20DESC'")

            # Esperando la respuesta del Servidor
            res = await websocket.recv()

            data = json.loads(res)

            test_logger.info(f"Respuesta del Server: {res}")

            assert data["event"] == "historico"
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_four(self, start_test_server, test_logger):
        """
        Este test se encarga de simular una interaccion entre la Pagina Web y el Servidor WebSokcet,
        Conectandose al Servidor con el Path (Ruta) `/dashboard` y el Parametro de Ruta (QueryParam) `value`

        **SENDS:**
            `Connection with path "/dashboard?value=Number&order=valor%20ASC"`

        **EXPECTS:**
            `(Objet with attribute "event") with a value "historico"`
            `(Object with attribute "data") with a data Type (list)`
        """
        uri = "ws://127.0.0.1:5000/dashboard?value=450&order=valor%20ASC"

        async with websockets.connect(uri, subprotocols=["None"]) as websocket:
            test_logger.info(f"Test Endpoint + QueryParam: '/dashboard?value=450&order=valor%20ASC'")

            # Esperando la respuesta del servidor
            res = await websocket.recv()

            data = json.loads(res)

            test_logger.info(f"Respuesta del Server: {res}")

            assert data["event"] == "historico"
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_five(self, start_test_server, test_logger):
        """
        Este test se encarga de probrar los filtros dentro de una sola conexion
        al WebSocket por ende, Se conectara y luego enviara mensaje con distintos cuerpos
        para manejar los filtros y Verificar su comportamiento.
        """
        uri = "ws://127.0.0.1:5000/dashboard"

        async with websockets.connect(uri, subprotocols=["None"]) as websocket:
            test_logger.info("Test de manejo de Filtros por JSON")

            mensaje1 = {
                "event": "historico",
                "order": {
                    "by": "timestamp",
                    "direction": "ASC"
                }
            }

            await websocket.send(json.dumps(mensaje1))

            test_logger.info(f"Test 1 Enviado: {mensaje1}")

            # Esperando respuesta
            res1 = await websocket.recv()

            test_logger.info(f"Respuesta del Server Mensaje 1: {res1}")

            data = json.loads(res1)

            assert data["event"] == "historico"
            assert isinstance(data["data"], list)

            mensaje2 = {
                "event": "historico",
                "filter": {
                    "date": "2025-03-12"
                },
                "order": {
                    "by": "timestamp",
                    "direction": "DESC"
                }
            }

            await websocket.send(json.dumps(mensaje2))

            test_logger.info(f"Test 2 Enviado: {mensaje2}")

            res2 = await websocket.recv()

            test_logger.info(f"Respuesta del Server Mensaje 2: {res2}")

            data = json.loads(res2)

            assert data["event"] == "historico"
            assert isinstance(data["data"], list)

            mensaje3 = {
                "event": "historico",
                "filter": {
                    "valor": "450"
                },
                "order": {
                    "by": "valor",
                    "direction": "ASC"
                }
            }

            await websocket.send(json.dumps(mensaje3))

            test_logger.info(f"Test 3 Enviado: {mensaje3}")

            res3 = await websocket.recv()

            test_logger.info(f"Respuesta del Server Mensaje 3: {res3}")

            data = json.loads(res3)

            assert data["event"] == "historico"
            assert isinstance(data["data"], list)