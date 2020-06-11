import requests

for i in range(50):
    r = requests.get("https://crunchy-bot.live/api/nsfw/hentai")
    try:
        print(r.json()['url'])
    except:
        pass