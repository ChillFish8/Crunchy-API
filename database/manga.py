import pymongo

from database.static import MongoDatabase


class MangaApi:
    def __init__(self, mongo_client: MongoDatabase):
        self.db = mongo_client.db
        self.anime: pymongo.collection.Collection = self.db['manga']
        self.anime.create_index([('english', pymongo.TEXT)])

    def search_anime(self, terms: str, limit: int):
        return list(self.anime.find({"$text": {'$search': terms}}, {'_id': 0}).limit(limit))
