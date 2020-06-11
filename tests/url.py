import requests, _thread

def ping():
    for i in range(50):
        r = requests.get("http://127.0.0.1/api/nsfw/hentai")
        print(r.json()['url'])


_thread.start_new_thread(ping, ())
_thread.start_new_thread(ping, ())
_thread.start_new_thread(ping, ())
_thread.start_new_thread(ping, ())
ping()
