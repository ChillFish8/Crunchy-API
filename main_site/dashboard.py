import jinja2_sanic
from sanic import response
from sanic.request import Request

from database.guild_data import GuildDatabase
from globals import Globals
from sanic_oauth.blueprint import fetch_user_guilds
from sanic_oauth.blueprint import login_required
from sanic_oauth.core import UserInfo

app = Globals.app
database = GuildDatabase()

UNAUTHORIZED = """<h1>⚠️ 403 — Unauthorized</h1><p>Requested URL {url} unauthorized</p>"""


async def check_perms(guilds, user_id):
    def check(guild):
        return guild

    return list(filter(check, guilds))


async def check_auth(guilds, guild_id):
    for guild in guilds:
        if int(guild['id']) == guild_id:
            return guild
    else:
        return False


async def get_guild(guilds, guild_id):
    for guild in guilds:
        if int(guild['id']) == guild_id:
            guild = {
                'id': guild['id'],
                'name': guild['name'],
                'icon': f'https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.webp?size=256',
                'prefix': '?',
                'premium': False,
                'nsfw': True,
                'release_hook': None,
                'news_hook': None
            }
            return guild


@app.route("/dashboard/main", methods=['GET'])
@login_required(provider="discord")
async def dashboard_home(request: Request, user_info: UserInfo):
    user_info = user_info.__dict__
    user_icon = f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'
    username = user_info['username']

    _, guilds = await fetch_user_guilds(request, provider="discord",
                                        oauth_endpoint_path="https://discord.com/api/users/@me/guilds")
    guilds = await check_perms(guilds, user_info['id'])

    guild_data = []
    for guild in guilds[:5]:
        guild_data.append(
            {
                'id': guild['id'],
                'name': guild['name'],
                'url': f'https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.webp?size=256',
                'href': f"'../server/{guild['id']}'"
            }
        )
    context = {
        'logged_in': True,
        'user': username,
        'icon': user_icon,
        'recent_guilds': guild_data[:2],
        'all_guilds': guild_data,

    }
    resp = jinja2_sanic.render_template("templates.dashboard_home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


async def get_server_request(request: Request, user_info: UserInfo, server_id: int):
    user_info = user_info.__dict__
    user_icon = f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'
    username = user_info['username']

    _, guilds = await fetch_user_guilds(
        request=request,
        provider="discord",
        oauth_endpoint_path="https://discord.com/api/users/@me/guilds")
    auth = await check_auth(guilds, server_id)
    if not auth:
        return response.html(status=403, body=UNAUTHORIZED.format(url=f"/server/{server_id}"))
    guilds = await check_perms(guilds, user_info['id'])
    guild = await get_guild(guilds, server_id)

    context = {
        'logged_in': True,
        'user': username,
        'icon': user_icon,
        'guild': guild,
    }
    resp = jinja2_sanic.render_template("templates.dashboard_server", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


async def post_server_update(request: Request, user_info: UserInfo, server_id: int):
    user_info = user_info.__dict__
    user_icon = f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'
    username = user_info['username']

    _, guilds = await fetch_user_guilds(
        request=request,
        provider="discord",
        oauth_endpoint_path="https://discord.com/api/users/@me/guilds")
    auth = await check_auth(guilds, server_id)
    if not auth:
        return response.html(status=403, body=UNAUTHORIZED.format(url=f"/server/{server_id}"))
    guilds = await check_perms(guilds, user_info['id'])
    guild = await get_guild(guilds, server_id)

    await database.update_webhook(guild_id=int(guild['id']), post_data=request.form)

    context = {
        'logged_in': True,
        'user': username,
        'icon': user_icon,
        'guild': guild,
    }
    resp = jinja2_sanic.render_template("templates.dashboard_server", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/server/<server_id:int>", methods=['GET', 'POST'])
@login_required(provider="discord")
async def server(request: Request, user_info: UserInfo, server_id):
    if request.method == "GET":
        return await get_server_request(request, user_info, server_id)
    elif request.method == "POST":
        return await post_server_update(request, user_info, server_id)