import jinja2_sanic
import jinja2
from sanic.exceptions import ServerError

from flisk import views


@views.register_path(name="api/endpoints", methods=['GET'])
async def endpoints(request):
    context = {}
    resp = jinja2_sanic.render_template("templates.endpoints", request, context)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
