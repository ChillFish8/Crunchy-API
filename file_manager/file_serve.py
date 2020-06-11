import os
import random


class FileManager:
    def __init__(self, base: str):
        self.base = base
        self.nsfw = os.listdir(f"{base}/nsfw/hentai")
        temp = {}
        for folder in self.nsfw:
            temp[folder] = []
            for file in os.listdir(f"{self.base}/nsfw/hentai/{folder}"):
                temp[folder].append(f"https://crunchy-bot.live/{self.base}/nsfw/hentai/{folder}/{file}")
        self.nsfw = temp

    def serve_file(self, endpoint, filename, area=None):
        areas = getattr(self, endpoint)
        if area is not None:
            area = areas.get(area, None)
        else:
            area = areas
        if area is None:
            raise IndexError("Area with name {}, is not in loaded areas.".format(area))
        return area.get(filename, None)

    def serve_random_file(self, endpoint, area=None):
        areas = getattr(self, endpoint)
        if area is not None:
            area = areas.get(area, None)
        else:
            area = areas.get(random.choice(tuple(areas.keys())))
        if area is None:
            raise IndexError("Area with name {}, is not in loaded areas.".format(area))
        return random.choice(area)
