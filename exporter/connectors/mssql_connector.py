import pymssql

from aes import decrypt
from typing import Any, List


class MSSqlConnector:
    connection = None
    cursor = None

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str = None,
        instancename: str = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.instancename = instancename

    def connect(self):
        self.connection = pymssql.connect(
            host=self.host,
            port=self.port,
            server=self.instancename,
            database=self.database,
            user=self.username,
            password=decrypt(self.password),
        )
        self.cursor = self.connection.cursor(as_dict=True)

    def execute(self, sql: str, data: List = []) -> Any:
        try:
            self.cursor.execute(
                sql,
                data,
            )
            self.connection.commit()
        except Exception as e:
            print(f'MSSql Error: {e}')
            self.connection.rollback()

    def fetchall(self, sql: str, data: List = []) -> Any:
        self.cursor.execute(
            sql,
            data,
        )
        return self.cursor.fetchall()

    def close(self) -> bool:
        self.cursor.close()
        self.connection.close()
