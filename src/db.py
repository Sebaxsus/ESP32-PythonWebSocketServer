import sqlite3, pathlib, datetime, logging

class Data_Base:
    def __init__(self, logger: logging.Logger, db_path: pathlib.Path):
        self.PATH = db_path
        self.conn = None
        self.logger = logger

    def __enter__(self):
        self.conn = sqlite3.connect(self.PATH, check_same_thread=False)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            
            self.conn.close()

    def init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                valor INTEGER
            )
        """)
        self.conn.commit()

    def insert_data(self, valor: int, local_timestamp: str) -> str:
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

            return "Ok"

        except Exception as e:
            # En caso de que falle (Excepcion) no hago ningun cambio en la bd
            self.conn.rollback()
            self.logger.exception(
                msg="Fallo la bd al insertar datos", 
                exc_info=e
            )
    
    def select_data(self) -> list[tuple[str, int]]:
        cursor = self.conn.execute("SELECT timestamp, valor FROM sensor_data ORDER BY timestamp DESC LIMIT 100")

        return cursor.fetchall()
    
    def get_db_path(self):
        return self.PATH

    def filter_by_date(self, date: str, ascendant: bool) -> list[tuple[str, int]]:
        order = "ASC" if ascendant else "DESC"

        cursor = self.conn.execute(
            f"SELECT timestamp, valor FROM sensor_data WHERE timestamp <= ? ORDER BY timestamp {order} LIMIT 100",
            (datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S"),)
        )

        return cursor.fetchall()

    def filter_by_value(self, value: int, ascendant: bool) -> list[tuple[str, int]]:
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