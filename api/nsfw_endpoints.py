import os

from flisk import views
from sanic import response
from globals import Globals

ALLOWED = [
    *os.listdir("data/nsfw")
]

@views.register_path(name="api/nsfw/hentai", methods=['GET'])
async def hentai_base_endpoint(request):
    tag = request.args.get('tag', None)
    if tag not in ALLOWED:
        tag = None
    url = Globals.file_manager.serve_random_file(endpoint="nsfw", area=tag)
    return response.json({'url': url})

