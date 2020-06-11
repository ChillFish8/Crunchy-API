import asyncio

from flisk import views
from sanic import response

from api.database import static
from api.database.manga import MangaApi
from api.database.static import pool

manga_info = MangaApi(static.db)


@views.register_path(name="api/manga/details", methods=['GET'])
async def manga_search_endpoint(request):
    terms = request.args.get('terms', None)
    legacy = request.args.get('legacy', False)
    limit = request.args.get('limit', 5)
    if terms is None:
        return response.empty(status=400)
    if limit > 15:
        limit = 15
    if legacy:
        data = await asyncio.get_event_loop()\
            .run_in_executor(pool, manga_info.search_anime, terms, limit)
        return response.json(data)
    else:
        data = await asyncio.get_event_loop()\
            .run_in_executor(pool, manga_info.search_anime, terms, limit)
        return response.json(data)