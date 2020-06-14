import jinja2_sanic
from sanic.request import Request

from globals import Globals
from sanic_oauth.blueprint import login_required
from sanic_oauth.core import UserInfo

app = Globals.app


@app.route("/dashboard/main", methods=['GET'])
@login_required(provider="discord")
async def dashboard_home(request: Request, user_info: UserInfo):
    user_info = user_info.__dict__
    user_icon = f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png'
    username = user_info['username']
    context = {
        'logged_in': True,
        'user': username,
        'icon': user_icon,
        'recent_guilds': [
            {
                'url': 'https://cdn.discordapp.com/icons/675647130647658527/61515ba4de15b723324b5d7cb8754ed1.webp?size=256',
                'name': "Crunchy's Room"
            },
            {
                'url': 'https://cdn.discordapp.com/icons/267624335836053506/a_0409ea649c9eb2aaaf3a5531a80a2528.webp?size=256',
                'name': "Python"
            },
            {
                'url': 'https://cdn.discordapp.com/icons/267624335836053506/a_0409ea649c9eb2aaaf3a5531a80a2528.webp?size=256',
                'name': "Python"
            },
        ],
    }
    resp = jinja2_sanic.render_template("templates.dashboard_home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
