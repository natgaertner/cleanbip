from utils.sql_utils import conn_curs,build_sql,write_json
from config import DATABASE_CONF,SCHEMA_TABLES,SCHEMA_ENUMS,SCHEMA_FKS,SCHEMA_SEQS,SCHEMA_TABLE_DICT

from utils.process_schema import rip_schema
from config import SCHEMA_FILE

def partition():
    from collections import OrderedDict
    from utils.create_partitions import create_flat_partitions
    from process_units import HIERARCHY,UNIT_DICT
    with conn_curs(DATABASE_CONF) as (connnection,cursor):
        for schema_table in SCHEMA_TABLES:
            create_flat_partitions(schema_table.name,('election_key','state_key'),HIERARCHY,UNIT_DICT,cursor)

def clean_schema():
    with conn_curs(DATABASE_CONF) as (connnection,cursor):
        for enum in SCHEMA_ENUMS:
            cursor.execute(enum.drop())
            cursor.execute(enum.sql())
        for seq in SCHEMA_SEQS:
            cursor.execute(seq.drop())
            cursor.execute(seq.sql())
        for table in SCHEMA_TABLES:
            cursor.execute(table.drop())
            cursor.execute(table.sql())

def dump_json(nulls=False):
    from config import json_location
    import os
    with conn_curs(DATABASE_CONF) as (connection,cursor):
        for schema_table in SCHEMA_TABLES:
            sql = build_sql(schema_table)
            cursor.execute(sql)
            write_json(cursor.fetchall(),os.path.join(json_location,schema_table.name+'.json'),nulls)
