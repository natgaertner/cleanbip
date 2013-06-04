from collections import OrderedDict

def create_discrete_partitions(table_names, partition_values, cursor, prev_children=[], prev_values=[], drop_old=False):
    pv = OrderedDict(partition_values)
    if len(pv) == 0:
        return
    else:
        k = pv.keys()[0]
        v_list = pv.pop(k)
        for t in table_names:
            for v in v_list:
                drop_sql = "DROP TABLE IF EXISTS {parent}_{value} CASCADE;".format(parent=t,value=v)
                create_sql = ("CREATE TABLE IF NOT EXISTS {parent}_{value} (CHECK (" + ' AND '.join("{child} = '{value}'".format(child=c, value=v) for c,v in zip(prev_children + [k], prev_values + [v])) +")) INHERITS ({parent});").format(parent=t, value=v)
                #print drop_sql
                print create_sql
                #cursor.execute(drop_sql)
                cursor.execute(create_sql)
                create_discrete_partitions([t+'_'+str(v)], pv, cursor, prev_children + [k], prev_values + [v],drop_old=drop_old)
            function_sql = ("CREATE OR REPLACE FUNCTION {parent}_insert_trigger() RETURNS TRIGGER AS $$ BEGIN IF "+ ' ELSEIF '.join("NEW.{child} = '{value}' THEN INSERT INTO {parent}_{value} VALUES (NEW.*);".format(parent=t,child=k, value=v) for v in v_list) + " ELSE RAISE EXCEPTION 'NO SUCH {child} IN DATABASE'; END IF; RETURN NULL; END; $$ LANGUAGE plpgsql;").format(parent=t, child=k)
            print function_sql
            cursor.execute(function_sql)
            drop_trigger_sql = 'DROP TRIGGER IF EXISTS insert_{parent}_trigger on {parent};'.format(parent=t)
            trigger_sql = 'CREATE TRIGGER insert_{parent}_trigger BEFORE INSERT on {parent} FOR EACH ROW EXECUTE PROCEDURE {parent}_insert_trigger();'.format(parent=t)
            print drop_trigger_sql
            print trigger_sql
            cursor.execute(drop_trigger_sql)
            cursor.execute(trigger_sql)


def create_flat_partitions(table_name, matching_fields, partition_order, units, cursor, drop_old=False):
    for partition_dict in permutation_tuple_generator(partition_order,units):
        ordered_values = tuple(partition_dict[po] for po in partition_order)
        suffix = '_'.join(ordered_values)
        drop_sql = "DROP TABLE IF EXISTS {table}_{values} CASCADE;".format(table=table_name,values=suffix)
        create_sql = ("CREATE TABLE IF NOT EXISTS {table}_{values} (CHECK (" + ' AND '.join("{field} = '{value}'".format(field=f, value=v) for f,v in zip(matching_fields,ordered_values)) +")) INHERITS ({table});").format(table=table_name, values=suffix)
        #print drop_sql
        print create_sql
        #cursor.execute(drop_sql)
        cursor.execute(create_sql)
    function_sql = "CREATE OR REPLACE FUNCTION {table}_insert_trigger() RETURNS TRIGGER AS $$ BEGIN {ifstatement} RETURN NULL; END; $$ LANGUAGE plpgsql;".format(table=table_name, ifstatement=trigger_else_generator(matching_fields,table_name,units,partition_order))
    print function_sql
    cursor.execute(function_sql)
    drop_trigger_sql = 'DROP TRIGGER IF EXISTS insert_{table}_trigger on {table};'.format(table=table_name)
    trigger_sql = 'CREATE TRIGGER insert_{table}_trigger BEFORE INSERT on {table} FOR EACH ROW EXECUTE PROCEDURE {table}_insert_trigger();'.format(table=table_name)
    print drop_trigger_sql
    print trigger_sql
    cursor.execute(drop_trigger_sql)
    cursor.execute(trigger_sql)

def permutation_tuple_generator(hierarchy,unit_dict,root={}):
    for k,v in unit_dict.iteritems():
        if v == None:
            yield dict(root.items() + {hierarchy[0]:k}.items())
        else:
            for t in permutation_tuple_generator(hierarchy[1:],v,dict(root.items() + {hierarchy[0]:k}.items())):
                yield t

def trigger_else_generator(matching_fields,table_name,unit_dict,hierarchy,ordered_values=()):
    return 'IF ' + (' ELSEIF '.join(("NEW.{field} = '{value}' THEN ".format(field=matching_fields[0],value=k) + trigger_else_generator(matching_fields[1:],table_name,v,hierarchy[1:],ordered_values+(k,)) if v != None else "NEW.{field} = '{value}' THEN INSERT INTO {table}_{suffix} VALUES (NEW.*);".format(field=matching_fields[0],value=k,table=table_name,suffix='_'.join(ordered_values+(k,)))) for k,v in unit_dict.iteritems()) + " ELSE RAISE EXCEPTION 'NO SUCH {field} IN DATABASE'; END IF;".format(field=hierarchy[0]))
