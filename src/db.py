import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).resolve().parent / "data.db"

class Data_Base:
    def __init__(self):
        self.PATH = DB_PATH

    def init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    valor INTEGER
                )
            """)

    def insert_data(self, valor, local_timestamp) -> str:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO sensor_data (timestamp, valor) VALUES (?, ?)", (local_timestamp, valor))
        return "Ok"
    
    def select_data(self) -> sqlite3.Cursor:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT timestamp, valor FROM sensor_data ORDER BY timestamp DESC LIMIT 100")
        return cursor
    
    def get_db_path(self):
        return DB_PATH
    
    def drop_table(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DROP TABLE sensor_data")