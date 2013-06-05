import os,re,subprocess

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

def cut(source,indexes,delimiter):
    with open(source,'rU') as source_file:
        #Use explicit columns and map of column names to cut indexes
        pipe = subprocess.Popen(['cut','-d',delimiter,'-f','1,{indexes}'.format(indexes=','.join(str(idx+1) for idx in indexes)),source],stdout=subprocess.PIPE)
        return pipe.stdout
