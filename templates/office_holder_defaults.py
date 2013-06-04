import table_defaults as td
from reformat import contest_id,referendum_id,ed_concat,concat_us,nowtime

class OfficeHolderTemplate():
    def __init__(self,election_key,state_key,office_holder_file_location,ed_map_function,source_prefix=None):
        self.tdt = td.TableDefaultTemplate(election_key,state_key,source_prefix,office_holder_file_location=office_holder_file_location)

        self.TABLES = {
            'OFFICE_IMPORT':dict(self.tdt.default_office_holder_table().items()+{
                'table':'office_import',
                'dict_reader':True,
                'columns':{
                    'identifier':{'function':concat_us,'columns':('Electoral District','Office Name')},
                    'id_long':{'function':concat_us,'columns':('Electoral District','Office Name')},
                    'office_level':'Office Level',
                    'state':'State',
                    'name':'Office Name',
                    'body_name':'Body Name',
                    'body_represents_state':'Body Represents - State',
                    'body_represents_county':'Body Represents - County',
                    'body_represents_muni':'Body Represents - Muni',
                    'source':'Source',
                    'updated':{'function':nowtime,'columns':()},
                    ('electoral_district_name', 'electoral_district_type','electoral_district_id_long','ed_matched'):{'function': ed_map_function, 'columns':('Electoral District',)},
                    }
                }.items()
            ),

            'OFFICE_HOLDER_IMPORT':dict(self.tdt.default_office_holder_table().items()+{
                'table':'office_holder_import',
                'dict_reader':True,
                'columns':{
                    'identifier':'UID',
                    'id_long':'UID',
                    'name':'Official Name',
                    'party':'Official Party',
                    'phone':'Phone',
                    'mailing_address':'Mailing Address',
                    'website':'Website',
                    'email':'Email',
                    'facebook_url':'Facebook URL',
                    'twitter_name':'Twitter Name',
                    'google_plus_url':'Google Plus URL',
                    'wiki_word':'Wiki Word',
                    'youtube':'Youtube',
                    'dob':'DOB',
                    'expires':'Expires',
                    'source':'Source',
                    'updated':{'function':nowtime,'columns':()},
                    }
                }.items()
            ),

            'OFFICE_HOLDER_TO_OFFICE_IMPORT':dict(self.tdt.default_office_holder_table().items() + {
                'table':'office_holder_to_office_import',
                'dict_reader':True,
                'columns':{
                    'office_holder_id_long':'UID',
                    'office_id_long':{'function':concat_us,'columns':('Electoral District','Office Name')},
                    },
                }.items()
            ),
        }
