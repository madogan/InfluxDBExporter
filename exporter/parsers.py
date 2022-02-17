import yaml

from models import Config, InfluxConnection, Job, DatabaseType, MSSqlConnection, OracleConnection


def parse_config(path: str) -> Config:
    config = Config()

    with open(path, 'rt') as fp:
        data = yaml.safe_load(fp.read())

    config.influx = InfluxConnection(**data['influx'])

    connections = {}

    for name, values in data['connections'].items():
        database_type = values.pop('database_type', None)
        if database_type == 'oracle':
            connections[name] = OracleConnection(name=name, **values)
        elif database_type == 'mssql':
            connections[name] = MSSqlConnection(name=name, **values)
        else:
            raise Exception(f'Unknown database type: {database_type}')

    for name, values in data['jobs'].items():
        connection_name = values.pop('connection_name')
        config.jobs[name] = Job(
            name=name, 
            connection=connections[connection_name], 
            **values
        )

    return config


if __name__ == '__main__':
    print(parse_config('config.yaml'))
