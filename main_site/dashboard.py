import jinja2_sanic
from sanic.request import Request

from flisk import views
from utils.discord_data import get_info


@views.register_path(name="dashboard/main", methods=['GET'])
async def dashboard_home(request: Request):
    user_token = request.ctx.__dict__['session'].get('token')
    username, user_icon = "Sign in", "../static//images/Discord-Logo-White.svg"
    if user_token:
        if not request.ctx.session.get('user'):
            user = await get_info(request=request)
            request.ctx.session['user'] = user
        else:
            user = request.ctx.session['user']
        user_icon = f'https://cdn.discordapp.com/avatars/{user["id"]}/{user["avatar"]}.png'
        username = user['username']
    context = {
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
            }
        ]
    }
    resp = jinja2_sanic.render_template("templates.dashboard_home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
