class ServiceName:
    '''names of infrastructure services'''
    messagebus = 'rabbit'
    cache = 'redis'
    database = 'mysql'
    email = 'gmail'

class InfrastructureService:
    '''configuration for a dependency'''
    name = ''
    connection = ''
    host = ''
    port = ''
    user = ''
    password = ''
    def __init__(self, name, connection, host, port, user, password):
        self.name = name
        self.connection = connection
        self.host = host
        self.port = port
        self.user = user
        self.password = password
