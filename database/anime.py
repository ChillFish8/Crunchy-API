import pymongo

from database.static import MongoDatabase


class AnimeApiLegacy:
    def __init__(self, mongo_client: MongoDatabase):
        self.db = mongo_client.db
        self.anime: pymongo.collection.Collection = self.db['anime']
        self.anime.create_index([('title', pymongo.TEXT)])

    def search_anime(self, terms: str, limit: int):
        return list(self.anime.find({"$text": {'$search': terms}}, {'_id': 0}).limit(limit))

class AnimeApi:
    def __init__(self, mongo_client: MongoDatabase):
        self.db = mongo_client.db
        self.anime: pymongo.collection.Collection = self.db['anime-info']
        self.anime.create_index([('english', pymongo.TEXT)])

    def search_anime(self, terms: str, limit: int):
        return list(self.anime.find({"$text": {'$search': terms}}, {'_id': 0}).limit(limit))
