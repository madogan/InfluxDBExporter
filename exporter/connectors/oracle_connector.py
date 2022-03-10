import os
import cx_Oracle

from typing import Any, List


class OracleConnector:
    connection = None
    cursor = None

    def __init__(
        self,
        host: str,
        port: int,
        sid: str,
        username: str,
        password: str
    ):
        self.host = host
        self.port = port
        self.sid = sid
        self.user = username
        self.password = password

        try:
            cx_Oracle.init_oracle_client(
                lib_dir=os.environ.get('LD_LIBRARY_PATH', 'C:\OracleClient'),
            )
        except Exception as e:
            print(f'Oracle Error: {e}')
            pass

    def connect(self) -> bool:
        # Create cx_Oracle connection.
        self.connection = cx_Oracle.connect(
            user=self.user, password=self.password, dsn=cx_Oracle.makedsn(
                host=self.host,
                port=self.port,
                sid=self.sid,
            ),
        )
        # Create cursor.
        self.cursor = self.connection.cursor()
    
    def execute(self, sql: str, data: List = []) -> Any:
        self.cursor.execute(
            sql,
            data,
        )
        self.connection.commit()

    def fetchall(self, sql: str, data: List = []) -> Any:
        print(f'Oracle: {sql}')
        self.cursor.execute(
            sql,
            data,
        )
        columns = [col[0] for col in self.cursor.description]
        self.cursor.rowfactory = lambda *args: dict(zip(columns, args))
        return self.cursor.fetchall()

    def close(self) -> bool:
        self.cursor.close()
        self.connection.close()
