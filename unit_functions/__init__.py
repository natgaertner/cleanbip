from utils.sql_utils import conn_curs
from config import DATABASE_CONF, SCHEMA_TABLE_DICT,SCHEMA_TABLES
import os

def compress_districts(unit):
    from config import locality_name,precinct_name,voterfile_delimiter,reduced_voterfile_name
    import csv
    from utils import cut
    from zipfile import ZipFile
    district_names = dict((e['name_column'],set()) for e in unit.ed_defs)
    district_names.update({locality_name:set(),precinct_name:set()})
    vf_columns = set(['voterbase_id']+[column for column_tuple in district_names for column in column_tuple if type(column_tuple) == tuple] + [column for column in district_names if type(column) == str])
    zfile = ZipFile(unit.UNCOMPRESSED_VOTER_FILE_ZIP_LOCATION)
    voter_file_name = zfile.namelist()[0]
    voter_file_full = os.path.join(unit.__path__[0],voter_file_name)
    if not os.path.exists(voter_file_full):
        zfile.extract(voter_file_name,unit.__path__[0])
    column_indexes = dict((column,idx) for idx,column in enumerate(open(voter_file_full).readline().split(voterfile_delimiter)) if column in vf_columns)

    extra_district_dicts = {}
    for k,v in (getattr(unit,'EXTRA_DISTRICTS',None) or {}).iteritems():
        edfile = os.path.join(unit.__path__[0],v['filename'])
        edcsv = csv.reader(open(edfile),delimiter='\t')
        edcsv.next()
        extra_district_dicts[k]=dict((l[0],l[v['column']-1]) for l in edcsv)
    
    with open(os.path.join(unit.__path__[0],reduced_voterfile_name),'w') as reduced_voterfile:
        reduced_voterfile_csv = csv.DictWriter(reduced_voterfile,fieldnames=column_indexes.keys() + extra_district_dicts.keys(),delimiter=voterfile_delimiter)
        reduced_voterfile_csv.writeheader()
        for i,line in enumerate(csv.DictReader(cut(voter_file_full,sorted(column_indexes.values()),voterfile_delimiter),delimiter=voterfile_delimiter)):
            write_line = False
            for edn,edd in extra_district_dicts.iteritems():
                line.update({edn,edd[line['voterbase_id']]})
            for name_columns,district_set in district_names.iteritems():
                if type(name_columns) == tuple:
                    name = tuple(line[nc] for nc in name_columns)
                else:
                    name = line[name_columns]
                if name not in district_set:
                    write_line = True
                    district_set.add(name)
            if write_line:
                reduced_voterfile_csv.writerow(line)
            if i % 100000 == 0:
                print i

def clean_import(unit):
    from utils.table_tools import import_table_sql,create_union_table_sql
    with conn_curs(DATABASE_CONF) as (connnection,cursor):
        for actual_table in unit.ACTUAL_TABLES:
            cursor.execute('DROP TABLE IF EXISTS {name} CASCADE;'.format(name=actual_table['import_table']))
            import_sql = import_table_sql(SCHEMA_TABLE_DICT[actual_table['schema_table']],actual_table)
            print import_sql
            cursor.execute(import_sql)

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

