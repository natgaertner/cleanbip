import districts
import os,imp,re,sys
if os.path.exists(os.path.join(__path__[0],'state_conf_data.py')):
    state_conf_data = imp.load_module('state_conf_data',*imp.find_module('state_conf_data',__path__))
else:
    from templates import state_conf_data
if os.path.exists(os.path.join(__path__[0],'ed_map.py')):
    ed_map = imp.load_module('ed_map',*imp.find_module('ed_map',__path__))
else:
    from templates import ed_map_template as ed_map

state_key = __path__[0].split(os.path.sep)[-1]
election_key = __path__[0].split(os.path.sep)[-2]
partition_suffixes = [election_key,state_key]
from templates.state_conf_template_office import StateConfTemplate
sct = StateConfTemplate(sys.modules[__name__],getattr(state_conf_data,'ed_defs',()),getattr(state_conf_data,'EXTRA_DISTRICTS',None),getattr(state_conf_data,'COUNTY_SCHOOL_DISTRICTS',False),getattr(state_conf_data,'COUNTY_JUDICIAL_DISTRICTS',False),getattr(state_conf_data,'ed_map_wrapper',None),getattr(state_conf_data,'VOTER_FILE_DISTRICTS',None))

for attr in dir(sct):
    if not attr.startswith('__'):
        setattr(sys.modules[__name__],attr,getattr(sct,attr))
