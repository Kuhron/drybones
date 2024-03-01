class Validated:
    def __init__(self, match=None):
        self.match = match
    
    def __bool__(self):
        return True


class Invalidated:
    def __init__(self, options=None):
        self.options = options

    def __bool__(self):
        return False


class Invalidation(Exception):
    pass
