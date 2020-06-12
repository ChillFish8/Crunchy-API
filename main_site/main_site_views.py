import jinja2_sanic
from sanic import response

from flisk import views


@views.register_path(name="api/endpoints", methods=['GET'])
async def endpoints(request):
    context = {}
    resp = jinja2_sanic.render_template("templates.endpoints", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@views.register_path(name="home", methods=['GET'])
async def home(request):
    context = {}
    resp = jinja2_sanic.render_template("templates.home", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@views.register_path(name="", methods=['GET'])
async def redirect_to_home(request):
    return response.redirect("home")
