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
        """
        Crea la tabla sensor_data en caso de que no exista
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                valor INTEGER
            )
        """)
        self.conn.commit()

    def insert_data(self, valor: int, local_timestamp: str) -> str:
        """
        Guarda los datos en la tabla sensor_data
        """
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
    
    def select_data(self, order: str|None) -> list[tuple[str, int]]:
        if not order:
            order = "timestamp DESC" # Manejando el caso de que no se mande order
            # Y estableciendo un orden por defecto
            
        cursor = self.conn.execute("SELECT timestamp, valor FROM sensor_data ORDER BY timestamp DESC LIMIT 100")

        return cursor.fetchall()
    
    def get_db_path(self):
        """
        Devuelve el path (Ruta) actual de la Base de Datos `.db`
        """
        return self.PATH

    def filter_by_date(self, date: str, order: str|None) -> list[tuple[str, int]]:
        if not order:
            order = "timestamp DESC" # Manejando el caso de que no se mande order
            # Y estableciendo un orden por defecto

        # Order terminaria siendo "timestamp DESC" o "valor ASC"
        cursor = self.conn.execute(
            f"SELECT timestamp, valor FROM sensor_data WHERE timestamp <= ? ORDER BY {order} LIMIT 100",
            (datetime.datetime.strptime(date, "%Y-%m-%d"),)
        )

        return cursor.fetchall()

    def filter_by_value(self, value: int, order: str|None) -> list[tuple[str, int]]:
        if not order:
            order = "timestamp DESC" # Manejando el caso de que no se mande order
            # Y estableciendo un orden por defecto
        
        cursor = self.conn.execute(
            f"SELECT timestamp, valor FROM sensor_data WHERE valor <= ? ORDER BY {order} LIMIT 100", 
            (value,)
        )
        # En caso de pruebas para logger toca guardar la respuesta de
        # la BD en Memoria (Variable), Para poder verla tanto en el logger
        # Como en el cliente, Por alguna razon si uso cursos.fetchall()
        # Accede a la respuesta de la BD y elimina su valor/Datos??? Es muy raro
        # Y en el server las siguientes llamadas a BD seran corruptas/Vacias
        # Es decir si accedo dos veces a cursor.fetchall() dentro de una misma
        # LLamada, las siguientes llamadas Estaran vacias???, Es muy RARO
        # Es como si dejara un promesa sin resolver y apenas pueda la resuelve, Por ende
        # La siguiente llamada ya estara resuelta y se volvera a dejar Pendiente
        # Como Digo muy raro.

        data = cursor.fetchall()
        self.logger.debug(f"Post Peticion a BD {value}, {order}, \t{data}")
        return data
        # return cursor.fetchall()
    
    def filter_by_data_and_value(self, date: str, value: int, order: str|None):
        if not order:
            order = "timestamp DESC" # Manejando el caso de que no se mande order
            # Y estableciendo un orden por defecto

        cursor = self.conn.execute(
            f"SELECT timestamp, valor FROM sensor_data WHERE timestamp <= ? AND valor <= ? ORDER BY {order} LIMIT 100",
            (date, value,)
        )

        return cursor.fetchall()

    def drop_table(self):
        self.conn.execute("DROP TABLE sensor_data")
        self.conn.commit()

    def close(self):
        self.conn.close()