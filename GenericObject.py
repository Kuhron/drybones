# so I can assign stuff to the ctx.obj with dot notation rather than string keys

class GenericObject:
    def __init__(self, dct=None):
        if dct is not None:
            for k,v in dct.items():
                setattr(self, k, v)
    
    def __repr__(self):
        return repr(self.__dict__)
