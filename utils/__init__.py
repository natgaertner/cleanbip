import os

def walklimit(root, level):
    root_tuple = (root.split(os.path.sep), [d for d in os.listdir(root) if os.path.isdir(os.path.join(root,d))], [f for f in os.listdir(root) if not os.path.isdir(os.path.join(root,f))])
    yield root_tuple
    if level > 0:
        for d in root_tuple[1]:
            for val in walklimit(os.path.join(root,d),level-1):
                yield val

def memoize(attr,cls=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            clz = cls or args[0]
            if kwargs.pop('overwrite',None) or not hasattr(clz,attr):
                setattr(clz,attr,f(*args,**kwargs))
            return getattr(clz,attr)
        return wrapped_function
    return decorator
