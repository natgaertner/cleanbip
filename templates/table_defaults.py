from utils import memoize
from config import voterfile_delimiter
class TableDefaultTemplate():
    def __init__(self, election_key, state_key, source_prefix=None, voter_file_location=None, candidate_file_location=None, election_file_location=None, referenda_file_location=None,office_holder_file_location=None):
        self.DEFAULT_TABLE = {
                'skip_head_lines':1,
                'format':'csv',
                'field_sep':',',
                'quotechar':'"',
                'copy_every':100000,
                'udcs':{
                    'election_key':election_key,
                    'state_key':state_key
                    },
                }
        self.DEFAULT_ACTUAL_TABLE = {
                'long_fields':(),
                'long_from':(),
                'long_to':(),
                }
        self.voter_file_location=voter_file_location
        self.candidate_file_location=candidate_file_location
        self.election_file_location=election_file_location
        self.referenda_file_location=referenda_file_location
        self.office_holder_file_location=office_holder_file_location
        self.source_prefix=source_prefix

    @memoize('DEFAULT_VF_TABLE')
    def default_vf_table(self,source='_vf',file_location=None):
        return self.specific_table((self.source_prefix or '') + source,file_location or self.voter_file_location)

    @memoize('DEFAULT_CANDIDATE_TABLE')
    def default_candidate_table(self,source='_ca',file_location=None):
        return self.specific_table((self.source_prefix or '') + source,file_location or self.candidate_file_location,',')

    @memoize('DEFAULT_OFFICE_HOLDER_TABLE')
    def default_office_holder_table(self,file_location=None):
        return dict(self.DEFAULT_TABLE.items() + {
            'filename':file_location or self.office_holder_file_location,
            'field_sep':',',
            }.items())

    @memoize('DEFAULT_REFERENDA_TABLE')
    def default_referenda_table(self,file_location=None):
        return self.specific_table('referenda',file_location or self.referenda_file_location,',')

    @memoize('DEFAULT_ELECTION_TABLE')
    def default_election_table(self,source='_elec',file_location=None):
        return self.specific_table((self.source_prefix or '') + source,file_location or self.election_file_location)

    def specific_table(self,source,file_location,field_sep=voterfile_delimiter):
        return dict(self.DEFAULT_TABLE.items() + {
            'filename':file_location,
            'field_sep':field_sep,
            'udcs':dict(self.DEFAULT_TABLE['udcs'].items()+{'source':source}.items()),
            }.items())

