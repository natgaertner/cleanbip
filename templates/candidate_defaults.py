import table_defaults as td
from reformat import contest_id,referendum_id,ed_concat,nowtime

class CandidateTemplate():
    def __init__(self,election_key,state_key,candidate_file_location,referenda_file_location,ed_map_function,source_prefix=None)
        self.tdt = td.TableDefaultTemplate(election_key,state_key,source_prefix,candidate_file_location=candidate_file_location,referenda_file_location=referenda_file_location)

        self.TABLES = {
            'CONTEST_IMPORT':dict(self.tdt.default_candidate_table().items()+{
                'udcs':dict(self.tdt.default_candidate_table()['udcs'].items() + {
                    'contest_type':'candidate',
                    }.items())
                'table':'contest_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'identifier':{'function':contest_id,'columns':(2,4,5)},
                    'id_long':{'function':contest_id,'columns':(2,4,5)},
                    'office_level':3,
                    'state':2,
                    'office':5,
                    ('electoral_district_name', 'electoral_district_type','electoral_district_id_long','ed_matched'):{'function': ed_map_function, 'columns':(4,)},
                    }
                }).items()
            ),

            'BALLOT_CONTEST_IMPORT':dict(self.tdt.default_referenda_table().items() + {
                'udcs':dict(self.tdt.default_candidate_table()['udcs'].items() + {
                    'contest_type':'referendum',
                    'electoral_district_type':'state',
                    'office':'statewide referendum',
                    'office_level':'Statewide',
                    'ed_matched':'True'
                    }.items())
                'filename':self.referendum_file_location,
                'table':'contest_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'identifier':{'function':referendum_id,'columns':(2,3)},
                    'id_long':{'function':referendum_id,'columns':(2,3)},
                    'state':2,
                    'electoral_district_name':2,
                    'electoral_district_id_long':{'function':ed_concat,'columns':(2,),'defaults':{'type':'state'}},
                    }
                }.items()
            ),

            'REFERENDUM_IMPORT':dict(self.tdt.default_referenda_table().items() + {
                'table':'referendum_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'identifier':{'function':referendum_id,'columns':(2,3)},
                    'id_long':{'function':referendum_id,'columns':(2,3)},
                    'contest_id_long':{'function':referendum_id,'columns':(2,3)},
                    'title':3,
                    'subtitle':4,
                    'brief':5,
                    'text':6,
                    }
                }.items()
            ),

            'BALLOT_RESPONSE_ONE_IMPORT':dict(self.tdt.default_referendum_table().items() + {
                'table':'ballot_response_one_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'referendum_id_long':{'function':referendum_id,'columns':(2,3)},
                    'identifier':{'function':concat_us,'columns':(2,3,7)},
                    'text':7,
                    }
                }.items()
            ),

            'BALLOT_RESPONSE_TWO_IMPORT':dict(self.tdt.default_referendum_table().items() + {
                'table':'ballot_response_one_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'referendum_id_long':{'function':referendum_id,'columns':(2,3)},
                    'identifier':{'function':concat_us,'columns':(2,3,8)},
                    'text':8,
                    }
                }.items()
            ),

            'CANDIDATE_IN_CONTEST_IMPORT':dict(self.tdt.default_candidate_table().items() + {
                'table':'candidate_in_contest_import',
                'columns':{
                    'candidate_id_long':1,
                    'contest_id_long':{'function':contest_id,'columns':(2,4,5)},
                    },
                }.items()
            ),

            'CANDIDATE_IMPORT':dict(self.tdt.default_candidate_table().items() + {
                'table':'candidate_import',
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'id_long':1,
                    'identifier':1,
                    #'office_level':3,
                    #'office_name':5,
                    'name':6,
                    'party':7,
                    'incumbent':9,
                    'phone':10,
                    'mailing_address':11,
                    'candidate_url':12,
                    'email':13,
                    'facebook_url':14,
                    'twitter_name':15,
                    'google_plus_url':16,
                    'wiki_word':17,
                    'youtube':18
                    },
                }.items()
            ),
        }

