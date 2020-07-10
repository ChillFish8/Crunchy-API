import asyncio
import base64
import concurrent.futures
import io
import random
import textwrap
from datetime import datetime
from string import ascii_letters, punctuation

import aiohttp
import discord
import requests
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from discord import Webhook, AsyncWebhookAdapter

from webhooks.webhook import GuildWebhooks
from webhooks.webhook_db import MongoDatabase

# Some constants we need to define before everything else.
ICON = "https://cdn.discordapp.com/app-icons/656598065532239892/39344a26ba0c5b2c806a60b9523017f3.png"

# Urls
API_BASE = "https://crunchy-bot.live/api/anime"

# Black list
EXCLUDE_IN_TITLE = [
    '(russian',
    '(spanish',
]

# Embed Option
DB_CONFIG = "database_config.json"
COLOUR = 0xe87e15
CR_LOGO = "https://cdn.discordapp.com/emojis/676087821596885013.png?v=1"
RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]
RANDOM_EMOJIS = [
    '<:thank_you:717784142053507082>',
    '<:cheeky:717784139226546297>',
    '<:exitment:717784139641651211>',
]

PFP_PATH = r'crunchy_image.png'

characters = list(ascii_letters) + list(punctuation)

def encode():
    random.shuffle(characters)
    file_name = "".join(characters[:11])
    new = str(base64.urlsafe_b64encode(file_name.encode("utf-8")), "utf-8").replace("=", "")
    return new

class MicroGuildWebhook:
    def __init__(self, guild_id, url, mentions=None):
        self.guild_id = guild_id
        self.url = url
        if mentions is not None:
            mentions = "__**Release Ping**__" + ", ".join(mentions)
        self.content = mentions


class WebhookBroadcast:
    def __init__(self, database: MongoDatabase, embed: discord.Embed,
                 web_hooks: list, type_: str, title: str, name="Crunchy"):
        self.embed = embed
        self.web_hooks = web_hooks
        self.failed_to_send = []
        self.session = None
        self.name = name
        self.type = type_
        self.successful = 0
        self.title = title
        self.database = database

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"Cleaning up broadcast, deleting {len(self.failed_to_send)} hooks.")
        for fail in self.failed_to_send:
            hook_object = GuildWebhooks(guild_id=fail, database=self.database)
            hook_object.delete_webhook(feed_type=self.type.lower())
        await self.session.close()

    async def send_func(self, hook: MicroGuildWebhook):
        try:
            webhook = Webhook.from_url(hook.url, adapter=AsyncWebhookAdapter(self.session))
            await webhook.send(embed=self.embed, content=hook.content, username=self.name)
            self.successful += 1

        except discord.NotFound:
            self.failed_to_send.append(hook.guild_id)

        except Exception as e:
            if str(e) == "Invalid webhook URL given.":
                self.failed_to_send.append(hook.guild_id)
            else:
                print(e)

    async def broadcast(self):
        chunks, remaining = divmod(len(self.web_hooks), 15)
        for i in range(chunks):
            tasks = []
            for guild in self.web_hooks[i * 15:i * 15 + 15]:
                if guild.url is not None:
                    tasks.append(self.send_func(hook=guild))
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)
            tasks = []
            for guild in self.web_hooks[::-1][:remaining]:
                if guild.url is not None:
                    tasks.append(self.send_func(hook=guild))
            await asyncio.gather(*tasks)
        self.title = self.title.replace('\n', '')
        print(f'[ {self.type} ] Completed broadcast of "{self.title}"!')
        print(f"[ {self.type} ]          {self.successful} messages sent!")


def map_objects_releases(data):
    data = data['config']
    id_ = data.get('guild_id', data.get('user_id', data.get('guid_id', )))
    guild = MicroGuildWebhook(id_, data['release'])
    return guild


def map_objects_news(data):
    data = data['config']
    id_ = data.get('guild_id', data.get('user_id', data.get('guid_id', )))
    guild = MicroGuildWebhook(id_, data['news'])
    return guild


class LiveFeedBroadcasts:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.database = MongoDatabase(DB_CONFIG)
        self.to_send = []
        self.sent = []
        self.processed_releases = []
        self.processed_news = []
        self.callbacks = {'release': self.release_callback, 'payload': self.news_callback}
        self.first_start = True

    async def release_callback(self, data):
        first = data['title'].split(" - ")[0]
        first = first.split("(")[0]
        terms = first.lower().replace(':', ' ').replace('-', '').split(" ")
        details = await self.get_release_info(terms=terms)
        if details is None:
            return
        else:
            anime_details = details['data']
            embed = self.make_release_embed(anime_details, data, data['title'].split(" - "))
            guilds = self.database.get_all_webhooks()
            web_hooks = list(map(map_objects_releases, guilds))
            async with WebhookBroadcast(
                    embed=embed, web_hooks=web_hooks, type_="RELEASES",
                    title=anime_details['title'], database=self.database) as broadcast:
                await broadcast.broadcast()

    @staticmethod
    def make_release_embed(details: dict, data: dict, first):
        embed = discord.Embed(
            title=f"{data['title']}", url=data.get('id', None), color=COLOUR)
        desc = f"⭐ **Rating:** {details['reviews']} / 5 stars\n" \
               f"[Read the reviews here!]" \
               f"({'https://www.crunchyroll.com/{}/reviews'.format(details['title'].lower().replace(' ', '-'))})\n" \
               f"\n" \
               f"📌 **[{first[1]}]({data['id']})**\n" \
               f"\n" \
               f"**Description:**\n" \
               f"{details.get('desc_long', 'No Description...')}\n"
        embed.description = desc
        embed.set_image(url=details['thumb_img'])
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        embed.set_footer(text="Anime releases from Crunchyroll. Bot powered by CF8")
        embed.set_author(name="Crunchyroll New Release! - Click for more!", url=data.get('id', None), icon_url=CR_LOGO)
        return embed

    @classmethod
    async def get_release_info(cls, terms: list):
        url = API_BASE + "/details?terms=" + "+".join(terms) + "&legacy=True"
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    if len(results) <= 0:
                        print(f"[ ERROR ] Api GET request failed to returned searched anime.")
                        return
                    else:
                        return results[0]
                else:
                    print(f"[ ERROR ] Api GET request failed with status {resp.status}")
                    return

    async def news_callback(self, data: dict):
        title = "\n".join(textwrap.wrap(data['title'], width=42))
        soup = BeautifulSoup(data['summary'].replace("<br/>", "||", 1).replace("\xa0", " "), 'lxml')
        split = soup.text.split("||", 1)
        summary, brief = split
        brief = "\n".join(textwrap.wrap(brief, width=50)[:6])
        brief += "..."
        img_url = soup.find('img').get('src')

        payload = {
            'title': title,
            'img_url': img_url,
            'summary': summary,
            'brief': brief,
            'url': data['id']
        }
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
            path = await asyncio.get_event_loop().run_in_executor(pool, self.generate_news_image, payload)
        print("Generated News with url: {}".format(path))
        await asyncio.sleep(20)
        embed = discord.Embed(
            description=f"[Read More]({payload['url']}) | "
                        f""
                        f" [Vote for Crunchy](https://top.gg/bot/656598065532239892)\n",
            color=0xe87e15,
            timestamp=datetime.now())
        embed.set_footer(text="Part of Crunchy, the Crunchyroll bot. Powered by CF8")
        embed.set_author(name="Crunchyroll Anime News! - Click for more!",
                         icon_url="https://cdn.discordapp.com/emojis/656236139862032394.png?v=1",
                         url=f"{payload['url']}")
        embed.set_image(url=path)

        guilds = self.database.get_all_webhooks()
        web_hooks = list(map(map_objects_news, guilds))

        await asyncio.sleep(60)
        async with WebhookBroadcast(
                embed=embed, web_hooks=web_hooks, type_="NEWS",
                title=payload['title'], database=self.database) as broadcast:
            await broadcast.broadcast()

    @staticmethod
    def generate_news_image(payload):
        original = Image.open("resources/webhooks/images/background.png")

        edited = ImageDraw.Draw(original)

        y_pos_diff = 35 * payload['title'].count("\n")
        title = payload['title']

        # Title
        edited.text((20, 20),
                    text=title,
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=32)
                    )

        # Episode / payload summary
        edited.text((20, (60 + y_pos_diff)),
                    text=f'''"{payload['summary']}"''',
                    fill=(102, 102, 102),
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial Italic/Arial Italic.ttf",
                        size=16)
                    )

        # Timestamp
        edited.text((20, (120 + y_pos_diff)),
                    text=datetime.now().strftime('%B, %d %Y %I:%M%p BST'),
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=18)
                    )

        # break line
        edited.line(((20, (145 + y_pos_diff)), (680, (145 + y_pos_diff))),
                    fill=(226, 226, 226),
                    width=1)

        # icon
        r = requests.get(payload['img_url'])
        buffer = io.BytesIO()
        buffer.write(r.content)
        buffer.seek(0)
        icon = Image.open(buffer)
        original.paste(icon, (20, 160 + y_pos_diff))

        # desc
        desc = payload['brief']
        edited.text((195, (160 + y_pos_diff)),
                    text=str(desc),
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=18)
                    )

        # Crunchy logo n stuff
        icon = Image.open(r"resources/webhooks/images/crunchy_image.png")
        icon = icon.resize((60, 60))
        original.paste(icon, (620, (70 + y_pos_diff)), icon)

        edited.text((350, (120 + y_pos_diff)),
                    text="Powered by Crunchy Discord bot.",
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=18)
                    )
        name = encode()
        original.save(f"data/news/{name}.png")
        return "https://crunchy-bot.live/" + f"data/news/{name}.png"
