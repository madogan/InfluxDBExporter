import datetime
import json
import re
import pytz
import requests

from typing import List


class APIConnector:
    session: requests.Session

    def __init__(
        self,
        url: str
    ) -> None:
        self.url = url
        
    def connect(self):
        self.session = requests.Session()
        self.session.trust_env = False
        
    def fetchall(self, endpoint, key, label):
        value = json.loads(self.session.get(f'{self.url}{endpoint}').text)[key]
        return [{ f'{str(label)}': value}]

    def close(self) -> bool:
        self.session.close()
