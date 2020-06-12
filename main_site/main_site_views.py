import jinja2_sanic
from sanic import response
from sanic.request import Request

from flisk import views
from utils.discord_data import get_guilds, get_info


@views.register_path(name="api/endpoints", methods=['GET'])
async def endpoints(request):
    context = {}
    resp = jinja2_sanic.render_template("templates.endpoints", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@views.register_path(name="home", methods=['GET'])
async def home(request: Request):
    user_token = request.ctx.__dict__['session'].get('token')
    if user_token:
        user = await get_info(request=request)
        print(user)
        _, guilds = await get_guilds(request=request)
        for guild in guilds:
            print(guild['name'])
    context = {}
    resp = jinja2_sanic.render_template("templates.home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@views.register_path(name="", methods=['GET'])
async def redirect_to_home(request):
    return response.redirect("home")
