import discord


class GuildWebhooks:
    def __init__(self, guild_id, database=None):
        """
        :param guild_id:
        :param database: -> Optional
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        On creation the class calls the data getting the guild webhooks
        this includes News and Release webhooks
        """
        self.guild_id = guild_id
        self._db = db if database is None else database
        self.data = self._db.get_guild_webhooks(guild_id=guild_id)
        self.news = self.data['news']
        self.release = self.data['release']

    def add_webhook(self, webhook: discord.Webhook, feed_type: str):
        if feed_type == "releases":
            self.release = webhook.url
        elif feed_type == "news":
            self.news = webhook.url
        else:
            raise NotImplementedError("No webhook option for {} type".format(feed_type))
        self._db.set_guild_webhooks(self.guild_id, self.to_dict())

    def delete_webhook(self, feed_type: str):
        if feed_type == "releases":
            self.release = None
        elif feed_type == "news":
            self.news = None
        else:
            raise NotImplementedError("No webhook option for {} type".format(feed_type))
        if self.news is None and self.release is None:
            self._db.delete_guild_webhooks(guild_id=self.guild_id)
        else:
            self._db.set_guild_webhooks(self.guild_id, self.to_dict())

    def to_dict(self):
        return {'user_id': self.guild_id,
                'news': self.news,
                'release': self.release
                }

