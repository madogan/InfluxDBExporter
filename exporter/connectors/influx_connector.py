from aes import decrypt
from typing import List
from influxdb import InfluxDBClient

class InfluxConnector:
    client = None

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def connect(self) -> bool:
        self.client = InfluxDBClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=decrypt(self.password),
        )
        
        # Get list of databases and check if database exists.
        # And swicth to the database.
        databases = self.client.get_list_database()
        databases = [str(d['name']) for d in databases]
        self.client.switch_database(self.database)

    def write_points(
        self, 
        points: List,
    ) -> bool:
        return self.client.write_points(points)
    
    def query(self, query: str) -> List:
        return self.client.query(query)

    def close(self) -> bool:
        self.client.close()
