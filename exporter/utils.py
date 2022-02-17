import datetime


def get_before_str_oracle(interval: datetime.timedelta) -> str:
    before = datetime.datetime.now() - interval
    return before.strftime("%d-%m-%Y %H:%M:%S")

def get_before_str_mssql(interval: datetime.timedelta) -> str:
    before = datetime.datetime.now() - interval
    return before.strftime("%Y-%m-%d %H:%M:%S")
