from config import script_settings
from state_abbr import states
import os,re,argparse
if not os.path.exists(script_settings['voterfiles']:
    os.mkdir(script_settings['voterfiles']
for state in states:
    vfs = [f for f in os.listdir('/home/vf_data/zipped_vfs') if re.match(script_settings['compressed_voterfile_pattern'],f)]
    vf = [f for f in vfs if re.search(r'_{state}_'.format(state=state.upper()),f)][0]
    if not os.path.exists(os.path.join(script_settings['voterfiles'],state.lower())):
        os.mkdir(os.path.join(script_settings['voterfiles'],state.lower()))
    if os.path.exists(os.path.join(script_settings['voterfiles'],state.lower(),vf)):
        os.remove(os.path.join(script_settings['voterfiles'],state.lower(),vf))
    os.link(os.path.join('/home/vf_data/zipped_vfs',vf),os.path.join(script_settings['voterfiles'],state.lower(),vf))
