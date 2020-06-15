from sanic_oauth.blueprint import fetch_user_info, fetch_user_guilds


async def get_info(request):
    user = await fetch_user_info(
        request,
        provider='default',
        oauth_endpoint_path="https://discord.com/api/users/@me",
        local_email_regex=request.app.config.OAUTH_EMAIL_REGEX)
    return user.__dict__


async def get_guilds(request):
    guilds = await fetch_user_guilds(
        request,
        provider='default',
        oauth_endpoint_path="https://discord.com/api/users/@me/guilds", )
    return guilds
