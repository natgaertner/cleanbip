import os
from utils.process_schema import rip_schema

script_settings = {
        'exception_state_configs':os.path.join(os.environ['BMS_HOME'],'exception_state_configs'),
        'exception_ed_maps':os.path.join(os.environ['BMS_HOME'],'exception_ed_maps'),
        'templates':os.path.join(os.environ['BMS_HOME'],'templates'),
        'candidates':os.path.join(os.environ['DROPBOX_HOME'],'BIP Production','candidates'),
        'office_holders':os.path.join(os.environ['DROPBOX_HOME'],'noBIP','office_holders'),
        'voterfiles':os.path.join(os.environ['BMS_HOME'],'voterfiles'),
        'voterfile_pattern':r'TS_Google.*\.txt',
        'compressed_voterfile_pattern':r'TS_Google.*\.zip',
        'process_units':os.path.join(os.environ['BMS_HOME'],'process_units'),
        }

#VOTER_FILE_SCHEMA = os.path.join(os.environ['BMS_HOME'],'schema','ts_voter_file.sql')
HIERARCHY = ['election','state']
timestamp_suffix = 'timestamped'
json_location = os.path.join(os.environ['BMS_HOME'],'json')
DATABASE_CONF = {
        'user':'postgres',
        'db':'cleanbip',
        'pw':os.environ['PGPASSWORD']
        }
SCHEMA_FILE = os.path.join(os.environ['BMS_HOME'],'config','office_holder_schema.sql')
SCHEMA_TABLES,SCHEMA_ENUMS,SCHEMA_FKS,SCHEMA_SEQS = rip_schema(SCHEMA_FILE)
SCHEMA_TABLE_DICT = dict((t.name,t) for t in SCHEMA_TABLES)
