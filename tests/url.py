import requests, _thread

def ping():
    for i in range(50):
        r = requests.get("https://crunchy-bot.live/api/nsfw/hentai?tag=tenticles")
        print(r.json()['url'])

ping()
