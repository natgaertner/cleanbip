DATABASE_CONFIG = {
        'user':'postgres',
        'db':'bip4',
        'pw':os.environ['PGPASSWORD']
        }
ERSATZPG_CONFIG = {
        'debug':True
        }
ERSATZPG_CONFIG.update(DATABASE_CONFIG)

