import os,imp,types
from utils import walklimit
from config import HIERARCHY
g = walklimit(__path__[0],len(HIERARCHY))
g.next()
UNIT_DICT = {}
MODULE_DICT = {}
for d in g:
    aligned_d0 = d[0][len(__path__[0].split(os.path.sep)):]
    add_to = UNIT_DICT
    add_to_module = MODULE_DICT
    for dr in aligned_d0[:-1]:
        add_to = add_to[dr]
        add_to_module = add_to_module[dr]
    if len(aligned_d0) == len(HIERARCHY):
        add_to[aligned_d0[-1]] = None
        add_to_module[aligned_d0[-1]] = imp.load_module(aligned_d0[-1],*imp.find_module(aligned_d0[-1],[os.path.join(p,*aligned_d0[:-1]) for p in __path__]))
    else:
        add_to[aligned_d0[-1]] = {}
        add_to_module[aligned_d0[-1]] = {}

def run_foreach_unit(func,unit_dict=UNIT_DICT,unit_path=tuple(__path__[0].split(os.path.sep)),include_units=(),exclude_units=(),**kwargs):
    if unit_dict is None:
        if (len(include_units) == 0 or unit_path in include_units) and (len(exclude_units) == 0 or not unit_path in exclude_units):
            func(unit_path,**kwargs)
    else:
        for k,v in unit_dict.items():
            run_foreach_unit(func,v,unit_path+(k,),include_units,exclude_units,**kwargs)

def yield_foreach_unit(func,unit_dict=UNIT_DICT,unit_path=tuple(__path__[0].split(os.path.sep)),include_units=(),exclude_units=(),**kwargs):
    if unit_dict is None:
        if (len(include_units) == 0 or unit_path in include_units) and (len(exclude_units) == 0 or not unit_path in exclude_units):
            yield func(unit_path,**kwargs)
    else:
        for k,v in unit_dict.items():
            for val in yield_foreach_unit(func,v,unit_path+(k,),include_units,exclude_units,**kwargs):
                yield val

def run_foreach_module(func,module_dict=MODULE_DICT,module_path=(),include_modules=(),exclude_modules=(),**kwargs):
    if type(module_dict)==types.ModuleType:
        if (len(include_modules) == 0 or module_path in include_modules) and (len(exclude_modules) == 0 or not module_path in exclude_modules):
            func(module_dict,**kwargs)
    else:
        for k,v in module_dict.items():
            run_foreach_module(func,v,module_path+(k,),include_modules,exclude_modules,**kwargs)

def yield_foreach_module(func,module_dict=MODULE_DICT,module_path=(),include_modules=(),exclude_modules=(),**kwargs):
    if type(module_dict)==types.ModuleType:
        if (len(include_modules) == 0 or module_path in include_modules) and (len(exclude_modules) == 0 or not module_path in exclude_modules):
            yield func(module_dict,**kwargs)
    else:
        for k,v in module_dict.items():
            for val in yield_foreach_module(func,v,module_path+(k,),include_modules,exclude_modules,**kwargs):
                yield val
