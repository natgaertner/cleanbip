"""
classes for representing sql table definitions:
    field:
        class representing a column in a sql table. Contains functions to create sql
        statement for creating the field (for insertion into table create statements). Will
        create extra field suffixed with "long" if this is a field referenced in a key and
        we are making short and long reference fields.

    table:
        class representing a sql table. Contains regexes for parsing a table definition out
        of sql and functions for creating an import version of the table (one with long keys)
        and a regular version of the table (one with sequence keys), functions for creating
        sequence key matches based on long key matches based on explicit actual table
        definitions in config, and some functions for doing the same based on fks in the
        schema def
    fk_constraint:
        class representing a foreign key contraint defined on a table. Contains regex for
        parsing a foreign key out of sql
    unique_constraint:
        class representing a unique constraint defined on a table. Contains regex for parsing
        a unique constraint out of sql and functions for creating unique constraint sql.
    enum:
        class representing an enum type. Contains regex for parsing out of sql.
    seq:
        class representing a sequence. Contains regex for parsing out of sql.



"""

import re, sys


class field:
    def __init__(self, name, stype, default=None):
        self.name = name
        self.type = stype
        self.default = default

    def sql(self):
        return '{name} {type}{default}'.format(name=self.name,type=self.type,default=(' DEFAULT {default_value}'.format(default_value=self.default) if self.default else ''))

class table:
    t_re = re.compile(r'(?P<constraint>\s*CONSTRAINT\s+(?:"?(?P<cname>\w+)"?)\s+UNIQUE\s+\((?P<ckeys>(?:\s*"?\w+"?\s*,?\s*)+)\)\s*,?)|(?P<pk>\s*PRIMARY\s+KEY\s*\((?P<pkeys>(?:\s*"?\w+"?\s*,?\s*)+)\)\s*,?)|(?P<field>\s*"?(?P<fname>\w+)"?\s+(?P<type>\w+(?:\(\d+\))?)(?:\s+DEFAULT\s+(?P<default>\w+(?:\(\'\w+\'\))?))?,?)')
    create_re = re.compile(r'\s*CREATE\s+TABLE\s+"?(\w+)"?\s*\((.+)\)')
    field_re = re.compile(r'\s*"?(?P<name>\w+)"?\s+(?P<type>\w+)(?:\s+DEFAULT\s+(?P<default>.+))?')
    pk_re = re.compile(r'\s*PRIMARY\s+KEY\s*\((.+)\)')
    def __init__(self):
        self.name = None
        self.fields = {} #dict of field objects
        self.primary_keys = [] #list of tuples. A tuple with multiple entries is a primary key on more than one field
        self.constraints = [] #unique constraints

    def sql(self, drop_keys=False,name_override=None,temp=False):
        elements = [f.sql() for f in self.fields.values()] + (['PRIMARY KEY ({pk})'.format(pk=','.join(pk)) for pk in self.primary_keys] if not drop_keys else []) + [c.sql() for c in self.constraints]
        return 'CREATE {temp} TABLE {name}({elements});'.format(name=name_override or self.name,elements = ','.join(elements),temp=('TEMP' if temp else ''))

    def drop(self):
        return 'DROP TABLE IF EXISTS {name} CASCADE;'.format(name=self.name)

class fk_constraint:
    fk_alter_re = re.compile(r'\s*ALTER\s+TABLE\s+?"(?P<from_table>\w+)"?\s+ADD\s+CONSTRAINT\s+(?:"?(?P<name>\w+)"?\s+)FOREIGN\s+KEY\s+\((?P<froms>.+)\)\s+REFERENCES\s+"?(?P<to_table>\w+)"?\s+\((?P<tos>.+)\)')
    def __init__(self):
        self.table = None #table that the constraint is on
        self.name = None #possibly empty name of constraint
        self.reference_table = None #table the key relates TO
        self.reference_fields = {} #dict of keys in from table to keys in to table

class unique_constraint:
    unique_re = re.compile(r'\s*CONSTRAINT\s+(?:"?(?P<name>\w+)"?)\s+UNIQUE\s+\((?P<fields>.+)\)')
    def __init__(self):
        self.table = None #table that the constraint is on
        self.name = None #possibly empty name of constraint
        self.fields = () #tuple of fields which must together be unique

    def sql(self):
        return 'CONSTRAINT{name} UNIQUE ({fields})'.format(name=' '+self.name if self.name else '',fields=','.join(self.fields))

class enum:
    enum_re = re.compile(r'\s*CREATE\s+TYPE\s+"?(\w+)"?\s+AS\s+ENUM\s+\((.+)\)')
    def __init__(self):
        self.name = None #enum name
        self.choices = () #possible enum values

    def sql(self):
        return 'CREATE TYPE {name} as ENUM {choices};'.format(name=self.name,choices=self.choices)

    def drop(self):
        return 'DROP TYPE IF EXISTS {name} CASCADE;'.format(name=self.name)

class seq:
    seq_re = re.compile(r'\s*CREATE\s+SEQUENCE\s+"?(\w+)"?\s+START\s+(\d+)\s*')
    def __init__(self):
        self.name = None #sequence name
        self.start = 1 #beginning of sequence

    def sql(self):
        return 'CREATE SEQUENCE {name} START {start};'.format(name=self.name,start=self.start)

    def drop(self):
        return 'DROP SEQUENCE IF EXISTS {name} CASCADE;'.format(name=self.name)

blank_re = re.compile(r'^\s*$')
choice_re = re.compile(r',?[\'"]?(\w+)[\'"]?')

#split on all delimiters that are not within parens. (parens are basically quotes)
def split_no_parens(string, delimiter=','):
    split = string.split(',')
    ret_split = []
    i = 0
    while i < len(split):
        s = split[i]
        ret_split.append(s)
        if s.count('(') > s.count(')'):
            while ret_split[-1].count('(') != s.count(')') and i != len(split)-1:
                i+=1
                s = split[i]
                ret_split[-1] += ','+s
        i+=1
    return ret_split

def objectify_statement(statement):
    """
    take a sql statement, turn it into the appropriate class, and add it to the collection of
    those objects. Boo side effects. Should just return object
    """
    m = enum.enum_re.match(statement)
    if m:
        e = enum()
        e.name = m.groups()[0]
        e.choices = tuple(n.groups()[0] for n in choice_re.finditer(m.groups()[1]))
        return e
    m = seq.seq_re.match(statement)
    if m:
        s = seq()
        s.name = m.groups()[0]
        s.start = int(m.groups()[1])
        return s
    m = fk_constraint.fk_alter_re.match(statement)
    if m:
        fk = fk_constraint()
        if m.groupdict().has_key('name'):
            fk.name = m.groupdict()['name']
        fk.table = m.groupdict()['from_table']
        fk.reference_table = m.groupdict()['to_table']
        fk.reference_fields = dict(zip((n.groups()[0] for n in choice_re.finditer(m.groupdict()['froms'])), (n.groups()[0] for n in choice_re.finditer(m.groupdict()['tos']))))
        return fk
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
        return t

def rip_schema(schema_file_name):
    """
    iterate through schema file, read to the end of each statement, then objectify it and add
    it to a list. return lists of objects of each type
    """
    with open(schema_file_name,'r') as schema_file:
        statement_objects = {table:[],enum:[],fk_constraint:[],seq:[]}
        statement = ''
        for l in schema_file:
            l = l.split('--')[0].strip()
            if blank_re.match(l):
                continue
            if ';' in l:
                l = l.split(';')
                for s in l[:-1]:
                    statement += ' '+s
                    statement_object = objectify_statement(statement)
                    statement_objects[statement_object.__class__].append(statement_object)
                    statement = ''
                statement += ' '+l[-1]
            else:
                statement += ' '+l
        return statement_objects[table],statement_objects[enum],statement_objects[fk_constraint],statement_objects[seq]

if __name__=='__main__':
    tables, enums, fks, seqs = rip_schema(sys.argv[1])
    tdict = dict([(t.name, t) for t in tables])
    print tdict['electoral_district__precinct'].primary_keys
