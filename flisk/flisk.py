import importlib

from sanic import Sanic

from flisk import views


class FliskApp(Sanic):
    """ This is the app class to start a flask app with
        flisk's custom wrapper ontop, allowing you to
        easily contain and distribute your views across
        files with a simple decorator system.
    """
    def __init__(self, name, settings):
        """ Settings should be a python file which contains:
                - REGISTERED_APPS : list
        """
        super().__init__(name)
        self.url_callbacks = {}
        self.modules = {}
        self.settings = settings

    def load(self):
        """ This should always be called, if you do not call
            this the system will not register **ANY** urls and you'll
            be left with a webserver doing litterally nothing.
        """
        apps = self.settings.REGISTERED_APPS
        for app_ in apps:
            loaded = importlib.import_module(app_)
            self.modules[loaded.__name__] = loaded

        registered_urls = views.Groupings.site_paths
        for url in registered_urls:
            print("Loading... {}".format(url))
            module, func = url.load
            located_app = self.modules[module]
            if len(func) == 1:   # Function based view
                func = func[0]
                if hasattr(located_app, func):
                    func_callback = getattr(located_app, func)
                    key = func_callback.path
                    kwargs = func_callback.kwargs
                    self.url_callbacks[key] = func_callback
                    self.add_route(func_callback, '/' + key, name=func_callback.name, **kwargs)
            elif len(func) == 2:  # Class based view
                if hasattr(located_app, func[0]):
                    class_ = getattr(located_app, func[0])
                    if hasattr(class_, func[1]):
                        class_ = class_()
                        func_callback = getattr(class_, func[1])
                        key = func_callback.path
                        kwargs = func_callback.kwargs
                        self.url_callbacks[key] = func_callback
                        self.add_route(func_callback, '/' + key, name=func_callback.name, **kwargs)
