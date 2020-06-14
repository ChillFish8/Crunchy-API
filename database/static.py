import concurrent.futures

from database.database import MongoDatabase

db = MongoDatabase(path="database_config.json")
pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
