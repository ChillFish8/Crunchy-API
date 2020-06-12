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
    context = {'user': username, 'icon': user_icon}
    resp = jinja2_sanic.render_template("templates.dashboard_home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
