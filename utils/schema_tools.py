
def delete_pksq(cursor,sequence_name):
    """
    delete key sequence
    """
    connection.cursor().execute('DROP SEQUENCE IF EXISTS {sequence_name} CASCADE;'.format(sequence_name=sequence_name))

def create_pksq(cursor,sequence_name,sequence_start):
    """
    create key sequence
    """
    connection.cursor().execute('CREATE SEQUENCE {sequence_name} START {sequence_start};'.format(sequence_name=sequence_name,sequence_start=sequence_start))

def delete_enum(cursor, enum_name):
    """
    delete enums
    """
    sql = "DROP TYPE IF EXISTS {enum_name} CASCADE;".format(enum_name=enum_name)
    connection.cursor().execute(sql)

def create_enum(cursor,enum_name,enum_values):
    """
    create enums
    """
    sql = "CREATE TYPE {enum_name} AS ENUM {enum_values};".format(enum_name=enum_name,enum_values=enum_values)
    connection.cursor().execute(sql)

def objectify_statement(statement, tables, enums, fks, seqs):
    """
    take a sql statement, turn it into the appropriate class, and add it to the collection of
    those objects. Boo side effects. Should just return object
    """
    m = enum.enum_re.match(statement)
    if m:
        e = enum()
        e.name = m.groups()[0]
        e.choices = tuple(n.groups()[0] for n in choice_re.finditer(m.groups()[1]))
        enums.append(e)
        return
    m = seq.seq_re.match(statement)
    if m:
        s = seq()
        s.name = m.groups()[0]
        s.start = int(m.groups()[1])
        seqs.append(s)

    m = fk_constraint.fk_alter_re.match(statement)
    if m:
        fk = fk_constraint()
        if m.groupdict().has_key('name'):
            fk.name = m.groupdict()['name']
        fk.table = m.groupdict()['from_table']
        fk.reference_table = m.groupdict()['to_table']
        fk.reference_fields = dict(zip((n.groups()[0] for n in choice_re.finditer(m.groupdict()['froms'])), (n.groups()[0] for n in choice_re.finditer(m.groupdict()['tos']))))
        fks.append(fk)
        return
    m = table.create_re.match(statement)
    if m:
        t = table()
        t.name = m.groups()[0]
        for n in table.t_re.finditer(m.groups()[1]):
            if n.groupdict()['pk']:
                t.primary_keys.append(tuple(o.groups()[0] for o in choice_re.finditer(n.groupdict()['pkeys'])))
            elif n.groupdict()['constraint']:
                uc = unique_constraint()
                uc.table = t.name
                uc.name = n.groupdict()['cname']
                uc.fields = tuple(o.groups()[0] for o in choice_re.finditer(n.groupdict()['ckeys']))
                t.constraints.append(uc)
            elif n.groupdict()['field']:
                t.fields[n.groupdict()['fname']] = field(n.groupdict()['fname'], n.groupdict()['type'], n.groupdict()['default'])
        tables[t.name] = t
        return

def rip_schema(schema_file_name):
    """
    iterate through schema file, read to the end of each statement, then objectify it and add
    it to a list. return lists of objects of each type
    """
    with open(schema_file_name,'r') as schema_file:
        tables = {}
        enums = []
        fks = []
        seqs = []
        statement = ''
        for l in schema_file:
            l = l.split('--')[0].strip()
            if blank_re.match(l):
                continue
            if ';' in l:
                l = l.split(';')
                for s in l[:-1]:
                    statement += ' '+s
                    objectify_statement(statement, tables, enums, fks, seqs)
                    statement = ''
                statement += ' '+l[-1]
            else:
                statement += ' '+l
        objectify_statement(statement, tables, enums, fks, seqs)
        return tables, enums, fks, seqs
