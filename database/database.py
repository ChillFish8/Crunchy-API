import json

import pymongo


class MongoDatabase:
    """
        This is the main Mongo DB class, this pull data from config.json and
        connects to the remote mongoDB (Falls back to local host if config missing)
        + Class Inherits:
    """

    def __init__(self, path):
        """
        This method requires no parameters, It takes all data from the
        class var `config`, if data is missing from config it falls
        back to the following settings:
        + host: localhost
        + port: 27017
        + user: root
        + password: root
        """

        with open(path, 'r') as file:
            self.config = json.load(file)
        addr = self.config.get('host_address', 'localhost')
        port = self.config.get('port', '27017')
        usr = self.config.get('username', 'root')
        pas = self.config.get('password', 'root')
        host = f"mongodb://{usr}:{pas}@{addr}:{port}/"

        self.client = pymongo.MongoClient(host)
        system_info = self.client.server_info()
        version = system_info['version']
        git_ver = system_info['gitVersion']
        print(f"Connected to {addr}:{port} from {self.client.HOST}, Version: {version}, Git Version: {git_ver}")

        self.db = self.client["Crunchy-Api"]
        # super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the data """
        self.db.logout()