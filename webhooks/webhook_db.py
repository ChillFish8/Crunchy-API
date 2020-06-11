import pymongo
import json


class GuildWebhooks:
    """ Custom Guild webhooks """

    def __init__(self, db):
        self.db = db
        self.guild_web_hooks = self.db["webhooks"]

    def set_guild_webhooks(self, guild_id: int, config: dict) -> [dict, int]:
        current_data = self.guild_web_hooks.find_one({'_id': guild_id})

        if current_data is not None:
            QUERY = {'_id': guild_id}
            new_data = {'config': config}
            resp = self.guild_web_hooks.update_one(QUERY, {'$set': new_data})
            return resp.raw_result
        else:
            data = {'_id': guild_id, 'config': config}
            resp = self.guild_web_hooks.insert_one(data)
            return resp.inserted_id

    def delete_guild_webhooks(self, guild_id: int):
        _ = self.guild_web_hooks.find_one_and_delete({'_id': f"{guild_id}"})
        return "COMPLETE"

    def get_guild_webhooks(self, guild_id: int) -> dict:
        current_data = self.guild_web_hooks.find_one({'_id': f"{guild_id}"})
        return current_data['config'] if current_data is not None else {'user_id': guild_id,
                                                                        'news': None,
                                                                        'release': None
                                                                        }

    def get_all_webhooks(self):
        all_ = self.guild_web_hooks.find({}, {'_id': 0})
        return list(all_)


class MongoDatabase(GuildWebhooks):
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

        self.db = self.client["Crunchy"]
        super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the data """
        self.db.logout()
