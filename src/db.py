import sqlite3, pathlib, datetime, logging

DB_PATH = pathlib.Path(__file__).resolve().parent / "data.db"

class Data_Base:
    def __init__(self, logger: logging.Logger):
        self.PATH = DB_PATH
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.logger = logger

    def init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                valor INTEGER
            )
        """)
        self.conn.commit()

    def insert_data(self, valor, local_timestamp) -> str:
        cursor = self.conn.cursor()
        try:
            # Iniciando la transaccion
            cursor.execute("BEGIN")
            # Ejecutando el comando en BD (Insert)
            cursor.execute(
                "INSERT INTO sensor_data (timestamp, valor) VALUES (?, ?)", 
                (local_timestamp, valor)
            )
            # Si llego aqui significa que no hubo ninguna excepcion por lo que terminare la transaccion con un commit
            self.conn.commit()

        except Exception as e:
            # En caso de que falle (Excepcion) no hago ningun cambio en la bd
            self.conn.rollback()
            self.logger.exception(
                msg="Fallo la bd al insertar datos", 
                exc_info=e
            )

        return "Ok"
    
    def select_data(self) -> list[tuple[str, int]]:
        cursor = self.conn.execute("SELECT timestamp, valor FROM sensor_data ORDER BY timestamp DESC LIMIT 100")

        return cursor.fetchall()
    
    def get_db_path(self):
        return DB_PATH

    def filter_by_date(self, date: str, ascendant: bool) -> list[tuple[str, int]]:
        order = "ASC" if ascendant else "DESC"

        cursor = self.conn.execute(
            f"SELECT timestamp, valor FROM sensor_data WHERE date <= ? ORDER BY timestamp {order} LIMIT 100",
            (datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S"),)
        )

        return cursor.fetchall()

    def filter_by_value(self, value: str, ascendant: bool) -> list[tuple[str, int]]:
        order = "ASC" if ascendant else "DESC"

        cursor = self.conn.execute(
            f"SELECT timestamp, valor FROM sensor_data WHERE valor <= ? ORDER BY timestamp {order} LIMIT 100", 
            (value,)
        )

        return cursor.fetchall()

    def drop_table(self):
        self.conn.execute("DROP TABLE sensor_data")
        self.conn.commit()

    def close(self):
        self.conn.close()