import jinja2_sanic
from sanic.request import Request

from globals import Globals
from sanic_oauth.blueprint import fetch_user_guilds
from sanic_oauth.blueprint import login_required
from sanic_oauth.core import UserInfo

app = Globals.app


@app.route("/dashboard/main", methods=['GET'])
@login_required(provider="discord")
async def dashboard_home(request: Request, user_info: UserInfo):
    user_info = user_info.__dict__

    user_icon = f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'
    username = user_info['username']

    user, guilds = await fetch_user_guilds(request, provider="discord",
                                           oauth_endpoint_path="https://discord.com/api/users/@me/guilds")
    guild_data = []
    for guild in guilds:
        guild_data.append(
            {
                'name': guild['name'],
                'url': f'https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.webp?size=256'
            }
        )
    context = {
        'logged_in': True,
        'user': username,
        'icon': user_icon,
        'recent_guilds': guild_data,
    }
    resp = jinja2_sanic.render_template("templates.dashboard_home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
