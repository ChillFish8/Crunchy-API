import pymongo
import random

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
        return list(self.anime.find({"$text": {'$search': terms, '$caseSensitive': False}}, {'_id': 0}).limit(limit))

    def get_daily(self):
        animes = list(self.anime.find({}, {'_id': 0}).limit(1024))
        random.shuffle(animes)
        return animes[:5]
