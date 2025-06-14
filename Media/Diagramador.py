from graphviz import Digraph
import pathlib
IMAGES_DIR = pathlib.Path(__file__).resolve().parent
# Diagrama 1: Flujo general del servidor WebSocket
server_flow = Digraph(comment="Flujo general del servidor WebSocket")
server_flow.attr(rankdir='LR', size='8')

server_flow.node('A', 'Cliente ESP/Web')
server_flow.node('B', 'Servidor WebSocket')
server_flow.node('C', 'Parseo del mensaje JSON')
server_flow.node('D', 'Identificar evento')
server_flow.node('E1', 'Guardar en SQLite', shape='box')
server_flow.node('E2', 'Enviar datos al cliente', shape='box')
server_flow.node('F', 'Cerrar conexión')

server_flow.edges([
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D'),
    ('D', 'E1'),
    ('D', 'E2'),
    ('E1', 'F'),
    ('E2', 'F')
])

# Diagrama 2: Flujo de los tests automáticos
test_flow = Digraph(comment="Flujo de los tests automáticos")
test_flow.attr(rankdir='TB')

test_flow.node('A', 'Iniciar Pytest')
test_flow.node('B', 'Fixture: iniciar servidor WebSocket')
test_flow.node('C', 'Esperar 5s')
test_flow.node('D', 'Ejecutar TestClient')
test_flow.node('E', 'Enviar JSON por WebSocket')
test_flow.node('F', 'Esperar respuesta')
test_flow.node('G', 'Verificar respuesta')
test_flow.node('H', 'Terminar servidor')
test_flow.node('I', 'pytest_terminal_summary')

test_flow.edges([
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D'),
    ('D', 'E'),
    ('E', 'F'),
    ('F', 'G'),
    ('G', 'H'),
    ('H', 'I')
])

# Diagrama 3: Estructura de módulos
module_structure = Digraph(comment="Estructura de módulos")
module_structure.attr(rankdir='TB')

module_structure.node('A', 'server.py')
module_structure.node('B', 'Logger')
module_structure.node('C', 'Data_Base')
module_structure.node('D', 'conftest.py')
module_structure.node('E', 'Testing_With_Pytest.py')

module_structure.edge('server.py', 'Logger')
module_structure.edge('server.py', 'Data_Base')
module_structure.edge('conftest.py', 'Logger')
module_structure.edge('conftest.py', 'server.py')
module_structure.edge('Testing_With_Pytest.py', 'conftest.py')
module_structure.edge('Testing_With_Pytest.py', 'Logger')

server_flow.render(IMAGES_DIR / 'server_flow', format='png', cleanup=False)
test_flow.render(IMAGES_DIR / 'test_flow', format='png', cleanup=False)
module_structure.render(IMAGES_DIR / 'module_structure', format='png', cleanup=False)

[
    IMAGES_DIR / "server_flow.png",
    IMAGES_DIR /  "/test_flow.png",
    IMAGES_DIR / "module_structure.png"
]
