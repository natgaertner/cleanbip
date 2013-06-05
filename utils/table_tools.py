
def import_table_sql(schema_table, actual_table, name_override=None):
    return 'CREATE TABLE {name} ({fields});'.format(name=(name_override or actual_table['import_table']), fields=','.join([f.sql() for f in schema_table.fields.values()] + ['{name} text'.format(name=f['long']) for f in actual_table['long_fields']] ))

def distinct_import_sql(actual_table):
    """
    pull distinct field names from actual table definition and run create table statements with distinct on clauses
    """
    sql = 'CREATE TEMP TABLE {import_table}_distinct as SELECT DISTINCT ON ({distinct_fields}) * from {import_table};'.format(distinct_fields=','.join(actual_table['distinct_on']), import_table=actual_table['import_table'])
    sql += 'DROP TABLE {import_table};'.format(import_table=actual_table['import_table'])
    sql += 'CREATE TABLE {import_table} as SELECT * from {import_table}_distinct;'.format(import_table=actual_table['import_table'])
    return sql

def create_union_table_sql(schema_table,union):
    sql = import_table_sql(schema_table, union['actual_table'])
    for c in union['components']:
        sql += 'ALTER TABLE {name} INHERIT {parent};'.format(name=c ,parent=union['actual_table']['import_table'])
    return sql

def update_timestamp_sql(actual_table,schema_table,partition_suffixes,timestamp_suffix):
    table_name = schema_table.name+''.join('_{suffix}'.format(suffix=suffix) for suffix in partition_suffixes)
    timestamp_table_name = table_name + timestamp_suffix
    ufields = set(schema_table.fields.keys())
    ufields.remove('updated')
    ufields = ','.join('{u}={table_name}.{u}'.format(u=u,table_name=timestamp_table_name) for u in ufields)
    test_fields = set(schema_table.fields.keys())
    test_fields.remove('updated')
    try:
        test_fields.remove('identifier')
    except Exception as error:
        import pdb;pdb.set_trace()
    for lfd in actual_table['long_fields']:
        test_fields.remove(lfd['real'])
    test_fields = ' or '.join('{table_name}.{u} IS DISTINCT FROM {timestamp_table_name}.{u}'.format(u=u,table_name=table_name,timestamp_table_name=timestamp_table_name) for u in test_fields)
    update_timestamp = 'update {table_name} set updated={timestamp_table_name}.updated from {timestamp_table_name} where {table_name}.identifier = {timestamp_table_name}.identifier and ({conditions});'.format(conditions=test_fields,table_name=table_name,timestamp_table_name=timestamp_table_name)
    update_other = 'update {table_name} set {ufields} from {timestamp_table_name} where {table_name}.identifier = {timestamp_table_name}.identifier;'.format(ufields=ufields,table_name=table_name,timestamp_table_name=timestamp_table_name)
    insert = 'insert into {table_name}({fields}) select {fields} from {timestamp_table_name} where {timestamp_table_name}.identifier not in (select identifier from {table_name} where identifier is not null);'.format(table_name=table_name,timestamp_table_name=timestamp_table_name,fields=','.join(schema_table.fields.keys()))
    delete = 'delete from {table_name} where {table_name}.identifier is null or {table_name}.identifier not in (select identifier from {timestamp_table_name});'.format(table_name=table_name,timestamp_table_name=timestamp_table_name,fields=','.join(schema_table.fields.keys()))
    return update_timestamp+update_other+insert+delete

def create_timestamp_table_sql(schema_table,partition_suffixes,timestamp_suffix):
    sql = schema_table.sql(name_override=schema_table.name + ''.join('_{suffix}'.format(suffix=suffix) for suffix in partition_suffixes) + timestamp_suffix,temp=True)
    return sql

#NOTE ONLY HANDLES SINGLE FIELD FKS RIGHT NOW
def rekey_import_sql(schema_table, actual_table, partition_suffixes,timestamp_suffix):
    long_field_dict = dict([(a['long'],a['real']) for a in actual_table['long_fields']])
    sql = 'INSERT INTO {name}'.format(name=schema_table.name) + ''.join('_{suffix}'.format(suffix=suffix) for suffix in partition_suffixes) + timestamp_suffix
    sql += '(' + ','.join([f.name for f in schema_table.fields.values() if not f.name in long_field_dict.values()] + [long_field_dict[a['local_key']] for a in actual_table['long_to']] + [long_field_dict[a] for a in actual_table['long_from']]) +')'
    sql += ' SELECT ' + ','.join(['fromtable.{name}'.format(name=f.name) for f in schema_table.fields.values() if not f.name in long_field_dict.values()] + ['totable{i}.{to_key} as {from_key}'.format(i=i, to_key=actual_table['long_to'][i]['real_to_key'], from_key=long_field_dict[actual_table['long_to'][i]['local_key']]) for i in range(len(actual_table['long_to']))] + ['fromtable.{name}'.format(name=long_field_dict[a]) for a in actual_table['long_from']])
    sql += ' from {from_table_name}'.format(from_table_name=actual_table['import_table']) + ' as fromtable '
    sql += ''.join(' left join {name}'.format(name=actual_table['long_to'][i]['to_table']) + ' as totable{i} on '.format(i=i) + 'lower(fromtable.{from_key}) = lower(totable{i}.{to_key})'.format(i=i,from_key=actual_table['long_to'][i]['local_key'],to_key=actual_table['long_to'][i]['to_key']) for i in range(len(actual_table['long_to'])))+';\n'
    return sql
