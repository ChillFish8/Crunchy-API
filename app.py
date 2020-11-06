import importlib
import jinja2
import jinja2_sanic
import os
from datetime import timedelta
from sanic_scheduler import SanicScheduler, task
from sanic_session import Session, InMemorySessionInterface

import globals
from file_manager.file_serve import FileManager
from flisk.flisk import FliskApp
from rss.process_rss_feeds import RSSFeed
from webhooks.broadcasts import LiveFeedBroadcasts

WEB_SERVER_DETAILS = importlib.import_module('server.settings')
FILE_BASE = "data"

app = FliskApp(name="Crunchy-Bot-Website", settings=WEB_SERVER_DETAILS)
app.session = Session(app, interface=InMemorySessionInterface())
globals.Globals.app = app
app.load()
app.static(f"/{FILE_BASE}", f"./{FILE_BASE}")
app.static("/static", "./static")


def get_templates():
    mapping = {}
    for file in os.listdir("templates"):
        if file.endswith(".html"):
            with open(f"templates/{file}", "r", encoding="UTF-8") as template:
                mapping[f"templates.{file}".replace(".html", "")] = template.read()

    return mapping


jinja2_sanic.setup(app, loader=jinja2.DictLoader(get_templates()))

scheduler = SanicScheduler(app)

file_manager = FileManager(base=FILE_BASE)
broadcast = LiveFeedBroadcasts()

globals.Globals.file_manager = file_manager

news_rss = RSSFeed(rss_url="https://www.crunchyroll.com/newsrss",
                   change_callback=broadcast.news_callback)
release_rss = RSSFeed(rss_url="http://feeds.feedburner.com/crunchyroll/rss/anime",
                      change_callback=broadcast.release_callback)


@task(timedelta(minutes=5))
async def update_rss(_):
    """Runs the function every 5 minutes."""
    await news_rss.check_update()
    await release_rss.check_update()


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=8000,
        access_log=False,
        debug=False,
    )
