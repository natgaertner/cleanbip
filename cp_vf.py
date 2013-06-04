from config import script_settings
from state_abbr import states
import os,re,argparse
for state in states:
    vf = [f for f in os.listdir('/home/gaertner/bip-data/data/voterfiles/{state}'.format(state=state.lower())) if re.match(script_settings['compressed_voterfile_pattern'],f)][0]
    if not os.path.exists(os.path.join(script_settings['voterfiles'],state.lower())):
        os.mkdir(os.path.join(script_settings['voterfiles'],state.lower()))
    if os.path.exists(os.path.join(script_settings['voterfiles'],state.lower(),vf)):
        os.remove(os.path.join(script_settings['voterfiles'],state.lower(),vf))
    os.link(os.path.join('/home/gaertner/bip-data/data/voterfiles/{state}'.format(state=state.lower()),vf),os.path.join(script_settings['voterfiles'],state.lower(),vf))
