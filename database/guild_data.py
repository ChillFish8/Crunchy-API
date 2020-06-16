import re

import pymongo

from database.static import db


class GuildWebhook:
    def __init__(self, guild_id, **kwargs):
        self.guild_id = guild_id
        self.release_hook = self.check(kwargs.get('release_hook', 'None'))
        self.news_hook = self.check(kwargs.get('news_hook', 'None'))

    @staticmethod
    def check(url):
        m = re.search(r'discordapp.com/api/webhooks/(?P<id>[0-9]{17,21})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})', url)
        if m is not None:
            data = m.groupdict()
            return f"https://discordapp.com/api/webhooks/{data['id']}/{data['token']}"
        else:
            return None

    @property
    def export(self):
        return {'_id': f"{self.guild_id}"}, \
               {'config': {
                   'guild_id': self.guild_id,
                   'news': self.news_hook,
                   'release': self.release_hook}}


class GuildSettings:
    def __init__(self, guild_id, **kwargs):
        self.guild_id = guild_id
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.data = kwargs

    @property
    def export(self):
        return {'_id': int(self.guild_id)}, \
               {'config': {
                   'guild_id': self.guild_id,
                   **self.data
               }}


class GuildDatabase:
    def __init__(self):
        self.db = db.db
        self.guild_settings: pymongo.collection.Collection = self.db['guilds']
        self.guild_webhooks: pymongo.collection.Collection = self.db['webhooks']

    async def process_server_post(self, guild_id, post_data, existing_data):
        if any(['news_hook' in list(post_data.keys()), 'release_hook' in list(post_data.keys())]):
            if (post_data.get('news_hook', ['None'])[0] != "None") and \
                    (post_data.get('release_hook', ['None'])[0] != "None"):
                if (post_data.get('news_hook') != existing_data['news_hook']) or \
                        (post_data.get('release_hook') != existing_data['release_hook']):
                    return await self.update_guild_settings(guild_id, post_data, existing_data)
            else:
                return
        elif any(['bot_prefix' in list(post_data.keys()), 'nsfw_enabled' in list(post_data.keys())]):
            if (post_data.get('bot_prefix') != existing_data['prefix']) or \
                    (post_data.get('nsfw_enabled') != existing_data['nsfw']):
                return await self.update_guild_settings(guild_id, post_data, existing_data)

    async def update_webhook(self, guild_id, post_data, existing):
        data = {
            'news_hook': post_data['news_hook'][0],
            'release_hook': post_data['release_hook'][0],
        }
        hook = GuildWebhook(guild_id, **data)
        query, data = hook.export
        existing = self.guild_webhooks.find_one(query)
        if existing is None:
            self.guild_webhooks.insert_one({**query, **data})
        else:
            config = existing['config']
            if hook.release_hook is not None:
                config['release'] = hook.release_hook
            if hook.news_hook is not None:
                config['news'] = hook.news_hook
            if not (hook.news_hook is None and hook.release_hook is None):
                self.guild_webhooks.find_one_and_update(query, {'$set': {'config': config}})

    async def update_guild_settings(self, guild_id, post_data, existing):
        if post_data.get('bot_prefix') is None and post_data.get('nsfw_enabled') is None:
            return existing
        data = {
            'prefix': post_data.get('bot_prefix', [existing['prefix']])[0],
            'premium': existing['premium'],
            'nsfw_enabled': bool(post_data.get('nsfw_enabled', existing['nsfw'])),
        }
        hook = GuildSettings(guild_id, **data)
        query, data = hook.export
        existing = self.guild_settings.find_one(query)
        if existing is None:
            print(existing)
            print(query, data)
            # self.guild_settings.insert_one({**query, **data})
        else:
            print(existing)
            print(query, data)
            config = existing['config']
