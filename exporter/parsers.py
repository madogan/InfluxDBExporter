import yaml

from models import Config, InfluxConnection, MSSqlConnection, OracleConnection, APIConnection, APIJob, DatabaseJob


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
        elif database_type == 'api':
            connections[name] = APIConnection(name=name, **values)
        else:
            raise Exception(f'Unknown database type: {database_type}')

    for name, values in data['jobs'].items():
        connection_name = values.pop('connection_name')
        connection = connections[connection_name]
        
        if type(connection) == APIConnection:
            config.jobs[name] = APIJob(
                name=name, 
                connection=connection, 
                **values
            )
        else:
            config.jobs[name] = DatabaseJob(
                name=name, 
                connection=connection, 
                **values
            )

    return config
