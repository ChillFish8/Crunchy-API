import os
from collections import defaultdict

import aiohttp
from sanic.request import Request
from sanic.response import HTTPResponse, redirect

from globals import Globals
from sanic_oauth.blueprint import oauth_blueprint, login_required
from sanic_oauth.core import UserInfo

app = Globals.app
app.blueprint(oauth_blueprint)
app.session_interface = app.session.interface

app.config.OAUTH_REDIRECT_URI = 'http://94.0.190.160/oauth'
app.config.OAUTH_SCOPE = 'email'
app.config.OAUTH_PROVIDERS = defaultdict(dict)

DISCORD_PROVIDER = app.config.OAUTH_PROVIDERS['discord']
DISCORD_PROVIDER['PROVIDER_CLASS'] = 'sanic_oauth.providers.DiscordClient'
DISCORD_PROVIDER['SCOPE'] = "identify email guilds"
DISCORD_PROVIDER['CLIENT_ID'] = '656598065532239892'
DISCORD_PROVIDER['CLIENT_SECRET'] = os.getenv("CLIENT_TOKEN")

app.config.OAUTH_PROVIDERS['default'] = DISCORD_PROVIDER


@app.listener('before_server_start')
async def init_aiohttp_session(sanic_app, _loop) -> None:
    sanic_app.async_session = aiohttp.ClientSession()


@app.listener('after_server_stop')
async def close_aiohttp_session(sanic_app, _loop) -> None:
    await sanic_app.async_session.close()


@app.middleware('request')
async def add_session_to_request(request):
    await request.app.session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    """ Save the User token to their session """
    try:
        await request.app.session_interface.save(request, response)
    except Exception as e:
        if isinstance(e, Exception):
            pass


@app.route('/login')
@login_required(provider='discord')
async def index(request: Request, user: UserInfo) -> HTTPResponse:
    """ Used for Logging in and being redirected to the original page after login. """
    tab = request.args.get('tab', 'home')
    return redirect(tab)
