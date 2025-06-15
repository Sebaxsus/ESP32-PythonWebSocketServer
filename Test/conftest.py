"""
Que es conftest.py y porque Pytest entiende este archivo por si solo
y por ende no es necesario importarlo en el Test:

## ¿Qué es `conftest.py`?

`conftest.py` es un archivo **RESERVADO** por `Pytest` para definir
**Fixtures y hooks globales**, Por esto no es necesario importarlo manualmente en
los test de `Pytest`, Ya que `Pytest` lo detecta automáticamente **si está en el mismo directorio
o en uno superior al test**

---

## ¿Qué son los `fixtures`?

Los `fixtures` en `pytest` son funciones que **Preparan datos o recursos** para tus pruebas y pueden compartirse entre múltiples test.
**EJEMPLO:**
```python
# conftest.py
import pytest
from src.Logger import Server_Logger
@pytest.fixture()
def test_logger():
    logger = Server_Logger(...)
    return logger
```

El usar `scope="module"` significa que se creara una vez por módulo de test.

**COMO USARLO DENTRO DE UN TEST:**
```python
# test.py
import pytest
def test_num(test_logger):
    test_logger.info("Iniciando test")
    assert sum_nums(2,2) == 2
    assert isinstance(sum_nums(2,2), int)

```

---

[Info en la Documentación de conftest.py](https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixture-functions)

[Info en la Documentación de Hooks](https://docs.pytest.org/en/stable/reference/reference.html#hooks)
"""

import pytest
import pathlib, os, subprocess, time, sys, datetime

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

from src.Logger import Server_Logger

logger = Server_Logger(BASE_DIR / "Test").get_Logger()

start_time = datetime.datetime.now()

# Fixture para instanciar el Logger para todos los test unitarios
@pytest.fixture(scope="session", autouse=True)
def test_logger():
    global logger
    return logger


# Fixture es una funcion especial de `pytest`
# Se encarga de preparar un entorno **Controlado y Reutilizable** para cada prueba
# Ejemplos:
#   Crear un archivo temporal (tmp_path_factory.mktemp) Esto es un [metodo/Funcion de Pytest](https://docs.pytest.org/en/stable/reference/fixtures.html#built-in-fixtures)
#   Conectar a una base de datos en memoria
#   Iniciar un cliente / Servidor
#   Cargar datos de prueba
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

pytest.TerminalReporter.summary_stats
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    summary = terminalreporter.build_summary_stats_line()
    passed = terminalreporter.stats.get("passed", [])
    failed = terminalreporter.stats.get("failed", [])
    skipped = terminalreporter.stats.get("skipped", [])

    global logger

    logger.info("📋 Resumen detallado del test:")
    logger.info(f"✅ Tests pasados: {len(passed)}")
    for test in passed:
        logger.info(f"  - {test.nodeid}")

    if failed:
        logger.warning(f"❌ Tests fallidos: {len(failed)}")
        for test in failed:
            logger.warning(f"  - {test.nodeid}")

    if skipped:
        logger.info(f"⚠️  Tests saltados: {len(skipped)}")
        for test in skipped:
            logger.info(f"  - {test.nodeid}")

    results = []
    for result in summary[0]:
        results.append(result[0])

    logger.info(f"{results} in {datetime.datetime.now() - start_time} s")

    # logger.info(f"⏱️  Tiempo total: {terminalreporter._duration:.2f}s")