import asyncio

from sanic import response
from flisk import views

from database import static
from database.manga import MangaApi, MangaApiLegacy, WebtoonApi
from database.static import pool


manga_info = MangaApi(static.db)
manga_legacy = MangaApiLegacy(static.db)
webtoon_info = WebtoonApi(static.db)

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
        data = await asyncio.get_event_loop() \
            .run_in_executor(pool, manga_legacy.search, terms, limit)
        return response.json(data)
    else:
        data = await asyncio.get_event_loop()\
            .run_in_executor(pool, manga_info.search, terms, limit)
        return response.json(data)


@views.register_path(name="api/webtoon/details", methods=['GET'])
async def webtoon_search_endpoint(request):
    terms = request.args.get('terms', None)
    limit = request.args.get('limit', 5)
    if terms is None:
        return response.empty(status=400)
    if limit > 15:
        limit = 15

    data = await asyncio.get_event_loop() \
        .run_in_executor(pool, webtoon_info.search, terms, limit)
    return response.json(data)
