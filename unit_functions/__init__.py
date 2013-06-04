from utils.sql_utils import conn_curs
from config import DATABASE_CONF, SCHEMA_TABLE_DICT,SCHEMA_TABLES

def clean_import(unit):
    from utils.table_tools import import_table_sql,create_union_table_sql
    with conn_curs(DATABASE_CONF) as (connnection,cursor):
        for actual_table in unit.ACTUAL_TABLES:
            cursor.execute('DROP TABLE IF EXISTS {name} CASCADE;'.format(name=actual_table['import_table']))
            import_sql = import_table_sql(SCHEMA_TABLE_DICT[actual_table['schema_table']],actual_table)
            print import_sql
            cursor.execute(import_sql)
        for union in unit.UNIONS:
            cursor.execute('DROP TABLE IF EXISTS {name} CASCADE;'.format(name=union['actual_table']['import_table']))
            union_sql = create_union_table_sql(SCHEMA_TABLE_DICT[union['actual_table']['schema_table']],union)
            cursor.execute(union_sql)

def make_ersatz_conf(unit):
    from templates.ersatz_config_template import ersatz_config_template
    from itertools import groupby
    return dict(ersatz_config_template.items() + {
        'tables':dict((import_table['table'],import_table) for import_table in unit.IMPORT_TABLES),
        'parallel_load':tuple({'tables':tuple(t['table'] for t in g[1]),'keys':{}} for g in groupby(sorted(unit.IMPORT_TABLES,key=lambda import_table:import_table['filename']),lambda import_table:import_table['filename'])),
        }.items()
        )

def build(unit):
    from ersatz import new_process_copies
    with conn_curs(DATABASE_CONF) as (connection,cursor):
        if not hasattr(unit,'ERSATZPG_CONFIG'):
            setattr(unit,'ERSATZPG_CONFIG',make_ersatz_conf(unit))
        new_process_copies(unit,connection)
    distinct(unit)
    union(unit)
    rekey(unit)

def distinct(unit):
    from utils.table_tools import distinct_import_sql
    with conn_curs(DATABASE_CONF) as (connection,cursor):
        for actual_table in unit.ACTUAL_TABLES:
            if actual_table.has_key('distinct_on') and len(actual_table['distinct_on']) > 0:
                cursor.execute(distinct_import_sql(actual_table))

def union(unit):
    from utils.table_tools import create_union_table_sql
    with conn_curs(DATABASE_CONF) as (connnection,cursor):
        for union in unit.UNIONS:
            cursor.execute('DROP TABLE IF EXISTS {name} CASCADE;'.format(name=union['actual_table']['import_table']))
            union_sql = create_union_table_sql(SCHEMA_TABLE_DICT[union['actual_table']['schema_table']],union)
            cursor.execute(union_sql)

def rekey(unit):
    from utils.table_tools import rekey_import_sql,create_timestamp_table_sql
    from config import timestamp_suffix
    with conn_curs(DATABASE_CONF) as (connection,cursor):
        cleared_tables = set()
        for schema_table in SCHEMA_TABLES:
            cursor.execute(create_timestamp_table_sql(schema_table,unit.partition_suffixes,timestamp_suffix))

        for table in unit.ACTUAL_TABLES:
            schema_table = SCHEMA_TABLE_DICT[table['schema_table']]
            if len(table['long_fields']) > 0:
                sql = rekey_import_sql(SCHEMA_TABLE_DICT[table['schema_table']],table, unit.partition_suffixes,timestamp_suffix)
                print sql
                cursor.execute(sql)
            else:
                sql = 'INSERT INTO {name}'.format(name=table['schema_table']) + ''.join('_{suffix}'.format(suffix) for suffix in unit.partition_suffixes) + timestamp_suffix + ' SELECT * FROM {import_table};'.format(import_table=table['import_table'])
                cursor.execute(sql)
        timestamp(unit,connection,cursor)

def timestamp(unit,connection,cursor):
    from config import timestamp_suffix
    from utils.table_tools import update_timestamp_sql
    schema_to_actual = get_unique_schema_to_actual(unit)
    for schema_table in SCHEMA_TABLES:
        table_name = schema_table.name+''.join('_{suffix}'.format(suffix=suffix) for suffix in unit.partition_suffixes)
        timestamp_table_name = table_name+timestamp_suffix
        if 'updated' in schema_table.fields:
            sql = update_timestamp_sql(schema_to_actual[schema_table.name],schema_table,unit.partition_suffixes,timestamp_suffix)
            cursor.execute(sql)
        else:
            clear_sql = 'DELETE from {name};'.format(name=table_name)
            cursor.execute(clear_sql)
            direct_update_sql = 'INSERT into {name} SELECT * from {timestamp_table};'.format(name=table_name,timestamp_table=timestamp_table_name)
            cursor.execute(direct_update_sql)

def get_unique_schema_to_actual(unit):
    mapping = {}
    for schema_table in SCHEMA_TABLES:
        match_actuals = [u['actual_table'] for u in unit.UNIONS if u['actual_table']['schema_table'] == schema_table.name] or [a for a in unit.ACTUAL_TABLES if a['schema_table'] == schema_table.name]
        assert len(match_actuals) <= 1
        if match_actuals:
            mapping[schema_table.name] = match_actuals[0]
    return mapping
