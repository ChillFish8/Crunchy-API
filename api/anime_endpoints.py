import asyncio

from flisk import views
from sanic import response

from api.database import static
from api.database.anime import AnimeApi, AnimeApiLegacy
from api.database.static import pool

anime_info = AnimeApi(static.db)
anime_info_legacy = AnimeApiLegacy(static.db)


@views.register_path(name="api/anime/details", methods=['GET'])
async def anime_search_endpoint(request):
    terms = request.args.get('terms', None)
    legacy = request.args.get('legacy', False)
    limit = request.args.get('limit', 5)
    if terms is None:
        return response.empty(status=400)
    if limit > 15:
        limit = 15
    if legacy:
        data = await asyncio.get_event_loop() \
            .run_in_executor(pool, anime_info_legacy.search_anime, terms, limit)
        return response.json(data)
    else:
        data = await asyncio.get_event_loop() \
            .run_in_executor(pool, anime_info.search_anime, terms, limit)
        return response.json(data)



