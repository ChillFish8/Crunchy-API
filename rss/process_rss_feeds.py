import feedparser
import aiohttp
import asyncio


class RSSFeed:
    def __init__(self, rss_url, change_callback):
        self.url = rss_url
        self.callback = change_callback
        self.previous_ids = []

    async def check_update(self):
        rss = await self._fetch_rss()
        if rss is None:
            return

        feed = await self._rss_to_dict(rss)
        if feed['id'] not in self.previous_ids:
            self.previous_ids.append(feed['id'])
            asyncio.get_event_loop().create_task(self.callback(feed))

    async def _fetch_rss(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(self.url) as resp:
                return await resp.text()

    @classmethod
    async def _rss_to_dict(cls, rss):
        feeds = feedparser.parse(rss)['entries']
        return feeds[0]


async def test(feed):
    print(feed)


async def main():
    rss = RSSFeed(rss_url="http://feeds.feedburner.com/crunchyroll/rss/anime", change_callback=test)
    await rss.check_update()

if __name__ == "__main__":
    asyncio.run(main())