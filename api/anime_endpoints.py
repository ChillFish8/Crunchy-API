import asyncio

from sanic import response

from database import static
from database.anime import AnimeApi, AnimeApiLegacy
from database.static import pool
from flisk import views
from api.utils import sort_results

from sanic_scheduler import task
from datetime import timedelta

anime_info = AnimeApi(static.db)
anime_info_legacy = AnimeApiLegacy(static.db)
daily_list = []


@task(timedelta(hours=24))
async def update_daily(_):
    global daily_list
    data = await asyncio.get_event_loop() \
        .run_in_executor(pool, anime_info_legacy.get_daily)
    daily_list = data


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
        print(terms)
        data = await asyncio.get_event_loop() \
            .run_in_executor(pool, anime_info_legacy.search_anime, terms, limit + 10)
    else:
        data = await asyncio.get_event_loop() \
            .run_in_executor(pool, anime_info.search_anime, terms, limit + 10)
    data = sort_results(data, terms, limit)
    return response.json(data)


@views.register_path(name="api/anime/daily", methods=['GET'])
async def daily_picks(request):
    return response.json(daily_list)
