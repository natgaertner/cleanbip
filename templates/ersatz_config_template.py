from config import DATABASE_CONF
ersatz_config_template = dict(DATABASE_CONF.items() + {
        'use_utf':True,
        'debug':True,
        'key_sources':{},
        }.items())
