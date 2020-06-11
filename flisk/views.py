import inspect

from flisk.utils import Extensions


class Groupings:
    """ This class acts a sort of global container, storing the list of endpoints """
    site_paths = []


class StandardEndpoint:
    """ This is the Endpoint class used for function only views,
        this is allows people who are less customised for class contained
        systems to still use the system easily.
    """

    def __init__(self, func, **kwargs):
        """ This mostly just handles the kwargs from the decorator and adds the route to a list
            this is so the main app in Flisk will detect the route and build a url path for it
            and then register it on the main_site.
        """
        self._name = kwargs.pop('name', None)
        if self._name is None:
            self._name = func.__name__
        self.pass_request = kwargs.pop('pass_request', False)
        self.kwargs = kwargs
        self.callback = func
        Groupings.site_paths.append(self)

    def __call__(self, *args, **kwargs):
        """ This is the pre process to see if we should pass the
            request data or not.
        """
        return self.callback(*args, **kwargs)

    def __str__(self):
        return self.callback.__name__

    @property
    def __name__(self):
        return str(self._name)

    @property
    def name(self):
        return self._name

    @property
    def is_class(self):
        return False

    @property
    def load(self):
        return self.callback.__module__, (self.callback.__name__,)

    @property
    def path(self):
        """ This generates the url path (Ignoring the base address), because
            this is for a function only it uses the function name *or* the name kwarg
            in the decorator to produce the endpoint.
        """
        url = "{base}".format(base=self._name)
        # details = inspect.getfullargspec(self.callback)
        # for arg_name in details.args:
        #    type_hinted = details.annotations.get(arg_name, str)
        #    if not issubclass(type_hinted, Extensions.Request):
        #        if issubclass(type_hinted, int):
        #            datatype = "int:"
        #        elif issubclass(type_hinted, float):
        #            datatype = "float:"
        #        elif issubclass(type_hinted, Extensions.Path):
        #            datatype = "path:"
        #        else:
        #            datatype = ""
        #        url += "/<{data_type}{name}>".format(data_type=datatype, name=arg_name)
        return url


class EmbededEndpoint:
    """ This is the Endpoint class used for Class contained functions,
        this allows you to organise your endpoints with a simple class
        inheriting the View class to get an endpoint like:
         - MyClass/myfunc
    """

    def __init__(self, func, **kwargs):
        """ This mostly just handles the kwargs from the decorator and adds the route to a list
            this is so the main app in Flisk will detect the route and build a url path for it
            and then register it on the main_site.
        """
        self._name = kwargs.pop('name', None)
        if self._name is None:
            self._name = func.__name__
        self.pass_request = kwargs.pop('pass_request', False)
        self.callback = func
        self.kwargs = kwargs
        Groupings.site_paths.append(self)

    def __call__(self, *args, **kwargs):
        """ This is the pre process to see if we should pass the
            request data or not.
        """
        return self.callback(*args, **kwargs)

    def __str__(self):
        return self.callback.__name__

    @property
    def name(self):
        return self._name

    @property
    def is_class(self):
        return False

    @property
    def load(self):
        return self.callback.__module__, (self.callback.__qualname__.split('.')[0], self.callback.__name__,)

    @property
    def path(self):
        """ This generates the url path (Ignoring the base address), because
            this is for a class it uses the classname as a route also, this allows
            you do have a class e.g Api and have the endpoints contained within for
            organisation purposes.
        """
        section = self.callback.__qualname__.lower().split('.')
        section[len(section) - 1] = self._name
        url = "{base}".format(base='/'.join(section))
        details = inspect.getfullargspec(self.callback)
        if 'self' in details.args:
            raise AttributeError("Function decorated must be a classmethod or staticmethod.")
        for arg_name in details.args:
            type_hinted = details.annotations.get(arg_name, str)
            if not issubclass(type_hinted, Extensions.Request) and str(arg_name) != "cls":
                if issubclass(type_hinted, int):
                    datatype = "int:"
                elif issubclass(type_hinted, float):
                    datatype = "float:"
                elif issubclass(type_hinted, Extensions.Path):
                    datatype = "path:"
                else:
                    datatype = ""
                url += "/<{data_type}{name}>".format(data_type=datatype, name=arg_name)
        return url


# Decorators
def register_path(name=None, cls=None, classview=False, **attrs):
    """ This is used as a decorator, it takes the function name and adds it to a list """
    if cls is None:
        if not classview:
            cls = StandardEndpoint
        else:
            cls = EmbededEndpoint

    def wrapper(func):
        """ Wraps the function and allows us to add kwargs just via the deco """
        if isinstance(func, StandardEndpoint):
            raise TypeError('Callback is already a endpoint.')
        return cls(func, name=name, **attrs)

    return wrapper


# View classes
class RouteView:
    """ This should be inherited by any class view
        This allows the endpoint class to get more meta data on
        the class itself and other things as and when they're needed.
    """
    ClassView = EmbededEndpoint

    @property
    def get_endpoint(self):
        """ This can be overwritten if endpoint is not the class name """
        return self.__qualname__
