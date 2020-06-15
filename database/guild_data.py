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
                   'user_id': self.guild_id,
                   'news': self.news_hook,
                   'release': self.release_hook}}


class GuildDatabase:
    def __init__(self):
        self.db = db.db
        self.guild_settings: pymongo.collection.Collection = self.db['guilds']
        self.guild_webhooks: pymongo.collection.Collection = self.db['webhooks']

    async def process_server_post(self, guild_id, post_data):
        if any(['news_hook' in list(post_data.keys()), 'release_hook' in list(post_data.keys())]):
            if (post_data.get('news_hook', ['None'])[0] != "None") and \
                    (post_data.get('release_hook', ['None'])[0] != "None"):
                return await self.update_webhook(guild_id, post_data)
            else:
                return
        elif any(['bot_prefix' in list(post_data.keys()), 'nsfw_enabled' in list(post_data.keys())]):
            return await self.update_webhook(guild_id, post_data)

    async def update_webhook(self, guild_id, post_data):
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
