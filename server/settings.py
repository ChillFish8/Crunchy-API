"""
The settings folder, This is where main.py pulls any settings like registering apps
or other paths.
"""

import os

CURRENT_WORKING_DIR = os.getcwd()

# settings

REGISTERED_APPS = [
    'api.anime_endpoints',
    'api.manga_endpoints',
    'api.nsfw_endpoints',
    'api.sfw_endpoints',
    'main_site.main_site_views',
    'main_site.login',
]
