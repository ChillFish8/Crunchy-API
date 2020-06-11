class Extensions:
    class Path:
        """ Represents a flask path type, this passes
        the extra url parts instead of treating it like a url
        """
        pass
    
    class Request:
        def __init__(self):
            self.headers = None  # dummy field
            self.data = None  # dummy field

        """ Represents the url request data """
        pass


if __name__ == '__main__':
    pass
