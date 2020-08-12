import pymongo

from database.static import MongoDatabase


class MangaApi:
    def __init__(self, mongo_client: MongoDatabase):
        self.db = mongo_client.db
        self.manga: pymongo.collection.Collection = self.db['manga']
        self.manga.create_index([('english', pymongo.TEXT)])

    def search(self, terms: str, limit: int):
        return list(
            self.manga
                .find({"$text": {'$search': terms, '$caseSensitive': False}},
                      {'score': {'$meta': 'textScore'}, "_id": 0})
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit))


class MangaApiLegacy:
    def __init__(self, mongo_client: MongoDatabase):
        self.db = mongo_client.db
        self.manga: pymongo.collection.Collection = self.db['manga-info']
        self.manga.create_index([('title', pymongo.TEXT)])

    def search(self, terms: str, limit: int):
        return list(
            self.manga
                .find({"$text": {'$search': terms, '$caseSensitive': False}},
                      {'score': {'$meta': 'textScore'}, "_id": 0})
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit))


class WebtoonApi:
    def __init__(self, mongo_client: MongoDatabase):
        self.db = mongo_client.db
        self.webtoon: pymongo.collection.Collection = self.db['webtoon']
        self.webtoon.create_index([('title', pymongo.TEXT)])

    def search(self, terms: str, limit: int):
        return list(
            self.webtoon
                .find({"$text": {'$search': terms, '$caseSensitive': False}},
                      {'score': {'$meta': 'textScore'}, "_id": 0})
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit)
        )
