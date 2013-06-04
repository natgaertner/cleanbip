import psycopg2 as psycopg
import psycopg2.extras as psyex
import os, sys, csv, json
from collections import OrderedDict,defaultdict
from datetime import datetime
import config

def db_connect(config=config.DATABASE_CONF):
    connstr = []
    if config.has_key('host'):
        connstr.append("host=%s" % config['host'])
    if config.has_key('port'):
        connstr.append("port=%s" % config['port'])
    if config.has_key('sslmode'):
        connstr.append("sslmode=%s" % config['sslmode'])
    connstr.append("dbname=%s user=%s password=%s" % (config['db'], config['user'], config['pw']))
    return psycopg.connect(' '.join(connstr))

class conn_curs():
    def __init__(self,config=config.DATABASE_CONF, commit_on_close=True, use_dict=True):
        self.config = config
        self.commit_on_close = commit_on_close
        self.use_dict = use_dict

    def __enter__(self):
        conn, curs = get_db_conn_curs(self.config,self.use_dict)
        self.conn = conn
        return conn,curs

    def __exit__(self, type, value, traceback):
        if type is None:
            if self.commit_on_close:
                self.conn.commit()
            return True
        else:
            self.conn.close()


def get_db_conn_curs(config=config.DATABASE_CONF, use_dict=True):
    conn = db_connect(config)
    if use_dict:
        return conn, conn.cursor(cursor_factory=psyex.RealDictCursor)
    else:
        return conn, conn.cursor()

def convert_date_sql(k,v,table=None):
    if v == 'timestamp':
        return "to_char({table}{k}, 'YYYY-MM-DD HH24:MI:SS') as {k}".format(k=k,table=(table+'.' if table else ''))
    elif v == 'date':
        return "to_char({table}{k}, 'YYYY-MM-DD') as {k}".format(k=k,table=(table+'.' if table else ''))
    else:
        return "{table}{k}".format(k=k,table=(table+'.' if table else ''))

def dump_json(nulls=False):
    connection = db_connect(config.BIP_DATABASE_CONF)
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    for table in ['candidate','contest','candidate_in_contest','electoral_district','referendum','ballot_response','election']:
        sql = build_sql(table)
        print sql
        cur.execute(sql)
        write_json(cur.fetchall(),table+'.json',nulls)


office_fields = ['contest.office','contest.office_level','contest.state as co_state','contest.identifier as co_identifier', 'contest.election_key as co_ek']
candidate_fields = ['candidate.name','candidate.identifier as ca_identifier','candidate.party','candidate.incumbent','candidate.phone','candidate.mailing_address','candidate.candidate_url','candidate.email','candidate.facebook_url','candidate.twitter_name','candidate.google_plus_url','candidate.wiki_word','candidate.youtube', 'candidate.source as ca_source','candidate.election_key as ca_ek']
precinct_fields = ['precinct.name','precinct.number', 'precinct.source as pr_source','precinct.identifier as pr_identifier','locality.name as locality_name','locality.type as locality_type', 'precinct.election_key as pr_ek']
electoral_district_fields = ['electoral_district.name','electoral_district.identifier as ed_identifier','electoral_district.type','electoral_district.source as ed_source', 'electoral_district.election_key as ed_ek']
ed_condition = [('electoral_district','name', 'is not', None)]
pr_condition = [('precinct','name','is not', None)]

def related_office(o_dict):
    return '{co_state} {office} {office_level} {co_ek}'.format(**o_dict)

def related_electoral_district(ed_dict):
    return '{state} {type} {name} {ed_ek}'.format(state=ed_dict['ed_source'].replace('VF',''), **ed_dict)

def related_candidate(ca_dict):
    return '{state} {name} {party} {ca_ek}'.format(state=ca_dict['ca_source'].replace('Candidates',''), **ca_dict)

def related_precinct(pr_dict):
    return '{state} {locality_name} {locality_type} {name} {number} {pr_ek}'.format(state=pr_dict['pr_source'].replace('VF',''), **pr_dict)

electoral_district_id_tuple = (('ed_source',lambda s: s.replace('VF','')), ('ed_ek',str),'ed_identifier')
electoral_district_url_tuple = ('state','election','idn')
def electoral_district_json(idn=None, state=None, election=None, typ=None, name=None):
    if not (idn or state):
        pass
        #raise Exception
    conditions=[]
    if idn:
        if type(idn) == list:
            conditions.append(('electoral_district','identifier','in',idn))
        else:
            conditions.append(('electoral_district','identifier','=',idn))
    if state:
        conditions.append(('electoral_district','source','=',state.upper()+'VF'))
    if election:
        conditions.append(('electoral_district','election_key','=',election))
    if typ:
        conditions.append(('electoral_district','type','=',typ))
    if name:
        conditions.append(('electoral_district','name','ilike',"%{name}%".format(name=name)))
    office_sql = build_sql('contest',office_fields + ['electoral_district.identifier as ed_identifier', 'electoral_district.source as ed_source','electoral_district.election_key as ed_ek'],[(None,'electoral_district','electoral_district_id','id')],conditions + ed_condition)
    candidate_sql = build_sql('candidate',candidate_fields + ['electoral_district.identifier as ed_identifier', 'electoral_district.source as ed_source','electoral_district.election_key as ed_ek'],[(None,'candidate_in_contest','id','candidate_id'),('candidate_in_contest','contest','contest_id','id'),('contest','electoral_district','electoral_district_id','id')],conditions + ed_condition)
    precinct_sql = build_sql('precinct',precinct_fields + ['electoral_district.identifier as ed_identifier', 'electoral_district.source as ed_source','electoral_district.election_key as ed_ek'],[(None,'locality','locality_id','id'),(None,'electoral_district__precinct','id','precinct_id'),('electoral_district__precinct','electoral_district','electoral_district_id','id')],conditions + ed_condition + pr_condition)
    electoral_district_sql = build_sql('electoral_district',electoral_district_fields,[],conditions + ed_condition)
    #related_sql = {'office':office_sql,'candidate':candidate_sql,'precinct':precinct_sql}
    related_sql = {'office':office_sql,'candidate':candidate_sql}
    results = run_sql(electoral_district_sql, related_sql, electoral_district_id_tuple)
    solr_results = {}
    for key, result in results.items():
        url_fields = extract_id(result,electoral_district_id_tuple,True)
        result_dict = electoral_district_solr_dict(result)
        result_dict.update({'url_query':'&'.join('{key}={value}'.format(key=k,value=v) for k,v in url_fields.items())})
        solr_results[key] = result_dict
    #solr_results = dict((key,electoral_district_solr_dict(result)) for key,result in results.items())
    return results,solr_results

office_id_tuple = (('co_ek',str),'co_identifier')
office_url_tuple = ('election','idn')
def office_json(idn=None, state=None, election=None, office_level=None, office=None):
    if not (idn or (state and (office_level or office))):
        pass
        #raise Exception
    conditions=[]
    if idn:
        if type(idn) == list:
            conditions.append(('contest','identifier','in',idn))
        else:
            conditions.append(('contest','identifier','=',idn))
    if state:
        conditions.append(('contest','state','=',state.upper()))
    if election:
        conditions.append(('contest','election_key','=',election))
    if office_level:
        conditions.append(('contest','office_level','=',office_level))
    if office:
        conditions.append(('contest','office','ilike',"%{office}%".format(office=office)))
    office_sql = build_sql('contest',office_fields,[],conditions)
    candidate_sql = build_sql('candidate',candidate_fields + ['contest.identifier as co_identifier', 'contest.state as co_state','contest.election_key as co_ek'],[(None,'candidate_in_contest','id','candidate_id'),('candidate_in_contest','contest','contest_id','id')],conditions)
    precinct_sql = build_sql('precinct',precinct_fields + ['contest.identifier as co_identifier', 'contest.state as co_state','contest.election_key as co_ek'],[(None,'locality','locality_id','id'),(None,'electoral_district__precinct','id','precinct_id'),('electoral_district__precinct','electoral_district','electoral_district_id','id'),('electoral_district','contest','id','electoral_district_id')],conditions + pr_condition)
    electoral_district_sql = build_sql('electoral_district',electoral_district_fields + ['contest.identifier as co_identifier', 'contest.state as co_state','contest.election_key as co_ek'],[('electoral_district','contest','id','electoral_district_id')],conditions + ed_condition)
    #related_sql = {'electoral_district':electoral_district_sql,'candidate':candidate_sql,'precinct':precinct_sql}
    related_sql = {'electoral_district':electoral_district_sql,'candidate':candidate_sql}
    results =  run_sql(office_sql, related_sql, office_id_tuple)
    solr_results = {}
    for key, result in results.items():
        url_fields = extract_id(result,office_id_tuple,True)
        result_dict = office_solr_dict(result)
        result_dict.update({'url_query':'&'.join('{key}={value}'.format(key=k,value=v) for k,v in url_fields.items())})
        solr_results[key] = result_dict
    #solr_results = dict((key,office_solr_dict(result)) for key,result in results.items())
    return results,solr_results

candidate_id_tuple = (('ca_ek',str),'ca_identifier')
candidate_url_tuple = ('election','idn')
def candidate_json(idn=None, state=None, election=None, office=None, office_level=None, name=None):
    if not (idn or (state and (office or office_level or name))):
        pass
        #raise Exception
    conditions=[]
    if idn:
        if type(idn) == list:
            conditions.append(('candidate','identifier','in',idn))
        else:
            conditions.append(('candidate','identifier','=',idn))
    if state:
        conditions.append(('candidate','source','=',state.upper()+"Candidates"))
    if election:
        conditions.append(('candidate','election_key','=',election))
    if office_level:
        conditions.append(('contest','office_level','=',office_level))
    if office:
        conditions.append(('contest','office','ilike',"%{office}%".format(office=office)))
    if name:
        conditions.append(('candidate','name','ilike',"%{name}%".format(name=name)))
    office_sql = build_sql('contest',office_fields + ['candidate.identifier as ca_identifier', 'candidate.source as ca_source','candidate.election_key as ca_ek'],[(None,'candidate_in_contest','id','contest_id'),('candidate_in_contest','candidate','candidate_id','id')],conditions)
    candidate_sql = build_sql('candidate',candidate_fields,[],conditions)
    electoral_district_sql = build_sql('electoral_district',electoral_district_fields + ['candidate.identifier as ca_identifier', 'candidate.source as ca_source','candidate.election_key as ca_ek'],[('electoral_district','contest','id','electoral_district_id'),('contest','candidate_in_contest','id','contest_id'),('candidate_in_contest','candidate','candidate_id','id')],conditions + ed_condition)
    related_sql = {'electoral_district':electoral_district_sql,'office':office_sql}
    precinct_map_fields = ['precinct_map.name','precinct_map.number','precinct_map.source','precinct_map.pr_identifier','precinct_map.locality_name','precinct_map.locality_type']
    precinct_sql = build_sql('precinct',precinct_fields + ['candidate_in_contest.candidate_id'],[(None,'locality','locality_id','id'),(None,'electoral_district__precinct','id','precinct_id'),('electoral_district__precinct','electoral_district','electoral_district_id','id'),('electoral_district','contest','id','electoral_district_id'),('contest','candidate_in_contest','id','contest_id')],pr_condition)
    precinct_sql = 'create temp table precinct_map as ' + precinct_sql;
    final_precinct_sql = build_sql('precinct_map',precinct_map_fields + ['candidate.identifier as ca_identifier', 'candidate.source as ca_source','candidate.election_key as ca_ek'],[(None, 'candidate','candidate_id','id')],conditions)
    #results = run_sql(candidate_sql, related_sql, 'ca_identifier', {'precinct':(precinct_sql, final_precinct_sql)})
    results = run_sql(candidate_sql, related_sql, candidate_id_tuple)
    solr_results = {}
    for key, result in results.items():
        url_fields = extract_id(result,candidate_id_tuple,True)
        result_dict = candidate_solr_dict(result)
        result_dict.update({'url_query':'&'.join('{key}={value}'.format(key=k,value=v) for k,v in url_fields.items())})
        solr_results[key] = result_dict
    #solr_results = dict((key,candidate_solr_dict(result)) for key,result in results.items())
    import pdb;pdb.set_trace()
    return results,solr_results

precinct_id_tuple= (('pr_source',lambda s:s.replace('VF','')),('pr_ek',str),'pr_identifier')
precint_url_tuple = ('state','election','idn')
def precinct_json(idn=None, state=None, election=None, locality=None, name=None, number=None):
    if not (idn or (state and (locality or number or name))):
        pass
        #raise Exception
    conditions=[]
    if idn:
        if type(idn) == list:
            conditions.append(('precinct','identifier','in',idn))
        else:
            conditions.append(('precinct','identifier','=',idn))
    if state:
        conditions.append(('precinct','source','=',state.upper()+'VF'))
    if election:
        conditions.append(('precinct','election_key','=',election))
    if locality:
        conditions.append(('locality','name','=',locality))
    if number:
        conditions.append(('precinct','number','=',number))
    if name:
        conditions.append(('electoral_district','name','ilike',"%{name}%".format(name=name)))
    office_sql = build_sql('contest',office_fields + ['precinct.identifier as pr_identifier', 'precinct.source as pr_source','precinct.election_key as pr_ek'],[(None,'electoral_district','electoral_district_id','id'),('electoral_district','electoral_district__precinct','id','electoral_district_id'),('electoral_district__precinct','precinct','precinct_id','id')],conditions + pr_condition)
    precinct_sql = build_sql('precinct',precinct_fields,[(None,'locality','locality_id','id')],conditions + pr_condition)
    electoral_district_sql = build_sql('electoral_district',electoral_district_fields + ['precinct.identifier as pr_identifier', 'precinct.source as pr_source','precinct.election_key as pr_ek'],[(None,'electoral_district__precinct','id','electoral_district_id'),('electoral_district__precinct','precinct','precinct_id','id')],conditions + ed_condition + pr_condition)
    related_sql = {'office':office_sql,'electoral_district':electoral_district_sql}
    candidate_sql = build_sql('candidate',candidate_fields + ['electoral_district__precinct.precinct_id','candidate.identifier'],[(None,'candidate_in_contest','id','candidate_id'),('candidate_in_contest','contest','contest_id','id'),('contest','electoral_district','electoral_district_id','id'),('electoral_district','electoral_district__precinct','id','electoral_district_id')],[])
    candidate_sql = 'create temp table candidate_map as ' + candidate_sql
    candidate_final_sql = build_sql('candidate_map',[c.replace('candidate.','candidate_map.') for c in candidate_fields] + ['precinct.identifier as pr_identifier', 'precinct.source as pr_source','precinct.election_key as pr_ek'],[(None, 'precinct','precinct_id','id')],conditions+pr_condition)
    results = run_sql(precinct_sql, related_sql, precinct_id_tuple,{'candidate':(candidate_sql,candidate_final_sql)})
    solr_results = {}
    for key, result in results.items():
        url_fields = extract_id(result,precinct_id_tuple,True)
        result_dict = precinct_solr_dict(result)
        result_dict.update({'url_query':'&'.join('{key}={value}'.format(key=k,value=v) for k,v in url_fields.items())})
        solr_results[key] = result_dict
    #solr_results = dict((key,precinct_solr_dict(result)) for key,result in results.items())
    return results,solr_results

def electoral_district_solr_dict(result):
    d = {}
    d['type'] = 'electoral district'
    d['state'] = result['ed_source'].replace('VF','')
    d['name'] = result['name'] or ''
    d['start_date'] = str(result['ed_ek']) or ''
    if result['type'] == 'county_council':
        d['group_names'] = [d['state'],result['type'], result['name'].split('_')[0], d['state'] + ' ' + result['name'].split('_')[0]+ ' ' + result['type']]
    else:
        d['group_names'] = [d['state'],result['type'], d['state'] + ' ' + result['type']]
    d['columns'] = ['BIP: ' + col for col in ['name','identifier','type','state']]
    d['related_offices'] = [related_office(o) for o in result['office']]
    d['related_people'] = [related_candidate(c) for c in result['candidate']]
    #d['related_precincts'] = [related_precinct(p) for p in result['precinct']]
    d['related_electoral_districts'] = [related_electoral_district(result)]
    d['contributors'] = ['BIP']
    return d

def office_solr_dict(result):
    d={}
    d['type'] = 'office'
    d['state'] = result['state'] or ''
    d['name'] = result['office'] or ''
    d['start_date'] = str(result['co_ek']) or ''
    d['group_names'] = [d['state'],result['office_level']] + [related_electoral_district(e) for e in result['electoral_district']]
    d['columns'] = ['BIP: ' + col for col in ['office','office_level','state']]
    d['related_electoral_districts'] = [related_electoral_district(e) for e in result['electoral_district']]
    d['related_people'] = [related_candidate(c) for c in result['candidate']]
    #d['related_precincts'] = [related_precinct(p) for p in result['precinct']]
    d['related_offices'] = [related_office(result)]
    d['contributors'] = ['BIP']
    return d

def candidate_solr_dict(result):
    d={}
    d['type']='person'
    d['party'] = result['party'] or ''
    d['state']= result['ca_source'].replace('Candidates','')
    d['name'] = result['name'] or ''
    d['group_names'] = [d['state'],result['party']] + [related_office(o) for o in result['office']]
    d['columns'] = ['BIP: ' + col for col in ['name','party','incumbent','phone','mailing_address','candidate_url','email','facebook_url','twitter_name','google_plus_url','wiki_word','youtube', 'state']]
    d['related_electoral_districts'] = [related_electoral_district(e) for e in result['electoral_district']]
    d['related_people'] = [related_candidate(result)]
    #d['related_precincts'] = [related_precinct(p) for p in result['precinct']]
    d['related_offices'] = [related_office(o) for o in result['office']]
    d['contributors'] = ['BIP']
    return d

def precinct_solr_dict(result):
    d={}
    d['type']='precinct'
    d['state']=result['pr_source'].replace('VF','')
    d['name']=result['name'] + ' ' + result['number']
    d['group_names'] = [d['state'],result['locality_name'] + ' ' + result['locality_type'], d['state'] + ' ' + result['locality_name'] + ' ' + result['locality_type']] + [related_electoral_district(e) for e in result['electoral_district']]
    d['columns'] = ['BIP: ' + col for col in ['name','number','locality_name','locality_type']]
    d['related_electoral_districts'] = [related_electoral_district(e) for e in result['electoral_district']]
    d['related_people'] = [related_candidate(c) for c in result['candidate']]
    d['related_precincts'] = [related_precinct(result)]
    d['related_offices'] = [related_office(o) for o in result['office']]
    d['contributors'] = ['BIP']
    return d

def extract_id(row,id_fields,return_dict=False):
    built_id = []
    for idf in id_fields:
        if type(idf)==str:
            built_id.append(row[idf])
        else:
            built_id.append(idf[1](row[idf[0]]))
    if return_dict:
        return dict(zip(id_fields,built_id))
    else:
        return '_'.join(built_id)

def extract_url(row,id_fields,url_fields):
    built_url = []
    for udf,idf in zip(url_fields,id_fields):
        if type(idf)==str:
            built_url.append('{udf}={idf}'.format(udf=udf,idf=row[idf]))
        else:
            built_url.append('{udf}={idf}'.format(udf=udf,idf=idf[1](row[idf[0]])))
    return '&'.join(built_url)

def run_sql(main_sql,related_sql,id_fields, special_related={}):
    connection = db_connect(config.BIP_DATABASE_CONF)
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    cur.execute(main_sql)
    main_results = dict((extract_id(row,id_fields), defaultdict(lambda:[],row)) for row in cur.fetchall())
    for typ,rs in related_sql.items():
        cur.execute(rs)
        for row in cur.fetchall():
            try:
                main_results[extract_id(row,id_fields)][typ].append(row)
            except:
                import pdb;pdb.set_trace()
    for typ,related_set in special_related.items():
        for query in related_set:
            cur.execute(query)
        for row in cur.fetchall():
            main_results[extract_id(row,id_fields)][typ].append(row)
    return main_results

def write_json(resultset,fileident,nulls=False):
    with open(fileident,'w') as f:
        if nulls:
            f.write(json.dumps(resultset))
        else:
            f.write(json.dumps(map(lambda d: dict((k,v) for k,v in d.iteritems() if v != None),resultset)))

def build_sql(schema_table, joins=[], dependencies={}):
    fields = dict((f.name,f.type) for f in schema_table.fields.values())
    table = schema_table.name
    fields = ','.join(convert_date_sql(k,v,table) for k,v in fields.iteritems())
    join_sql = ' '.join('join {ftable} on {table}.{local_key}={ftable}.{foreign_key}'.format(ftable=ftable,table=(ltable or table),local_key=local_key,foreign_key=foreign_key) for ltable,ftable,local_key,foreign_key in joins)
    dependency_sql = ('where ' if len(dependencies) > 0 else '') + ' and '.join('{ftable}.{fkey}={filterval}'.format(ftable=ftable,fkey=fkey,filterval=psycopg.extensions.QuotedString(str(filterval)).getquoted()) for ftable,fkey,filterval in dependencies)
    return 'SELECT {fields} from {table} '.format(fields=fields,table=table) + join_sql + ' ' + dependency_sql + ';'

def convert_date_sql(k,v,table=None):
    if v == 'timestamp':
        return "to_char({table}{k}, 'YYYY-MM-DD HH24:MI:SS') as {k}".format(k=k,table=(table+'.' if table else ''))
    elif v == 'date':
        return "to_char({table}{k}, 'YYYY-MM-DD') as {k}".format(k=k,table=(table+'.' if table else ''))
    else:
        return "{table}{k}".format(k=k,table=(table+'.' if table else ''))
