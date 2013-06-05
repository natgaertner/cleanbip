import os
from utils import memoize
from reformat import ed_concat,concat_us,nowtime
import table_defaults as td

DEFAULT_ED_DEFS = (
                {'district_import':'CONGRESSIONAL_DISTRICT_IMPORT','district_precinct_import':'CONGRESSIONAL_DISTRICT__PRECINCT_IMPORT','district_type':'congressional_district','import_table':'electoral_district_cd_import','dict_reader':True,'name_column':'vf_CD','precinct_join_import_table':'electoral_district__precinct_cd_import'},
                {'district_import':'JUDICIAL_DISTRICT_IMPORT','district_precinct_import':'JUDICIAL_DISTRICT__PRECINCT_IMPORT','district_type':'judicial_district','import_table':'electoral_district_jd_import','dict_reader':True,'name_column':'vf_judicial_district','precinct_join_import_table':'electoral_district__precinct_jd_import'},
                {'district_import':'SCHOOL_DISTRICT_IMPORT','district_precinct_import':'SCHOOL_DISTRICT__PRECINCT_IMPORT','district_type':'school_district','import_table':'electoral_district_schd_import','dict_reader':True,'name_column':'vf_school_district','precinct_join_import_table':'electoral_district__precinct_schd_import'},
                {'district_import':'STATE_REP_DISTRICT_IMPORT','district_precinct_import':'STATE_REP_DISTRICT__PRECINCT_IMPORT','district_type':'state_rep_district','import_table':'electoral_district_srd_import','dict_reader':True,'name_column':'vf_HD','precinct_join_import_table':'electoral_district__precinct_srd_import'},
                {'district_import':'STATE_SENATE_DISTRICT_IMPORT','district_precinct_import':'STATE_SENATE_DISTRICT__PRECINCT_IMPORT','district_type':'state_senate_district','import_table':'electoral_district_ssd_import','dict_reader':True,'name_column':'vf_SD','precinct_join_import_table':'electoral_district__precinct_ssd_import'},
                {'district_import':'COUNTY_COUNCIL_DISTRICT_IMPORT','district_precinct_import':'COUNTY_COUNCIL__PRECINCT_IMPORT','district_type':'county_council','import_table':'electoral_district_cc_import','dict_reader':True,'name_column':('vf_county_name','vf_county_council',),'precinct_join_import_table':'electoral_district__precinct_cc_import'},
                {'district_import':'COUNTY_IMPORT','district_precinct_import':'COUNTY__PRECINCT_IMPORT','district_type':'county','import_table':'electoral_district_c_import','dict_reader':True,'name_column':'vf_county_name','precinct_join_import_table':'electoral_district__precinct_c_import'},
                {'district_import':'STATE_IMPORT','district_precinct_import':'STATE__PRECINCT_IMPORT','district_type':'state','import_table':'electoral_district_s_import','dict_reader':True,'name_column':'vf_source_state','precinct_join_import_table':'electoral_district__precinct_s_import'},
                {'district_import':'TOWNSHIP_IMPORT','district_precinct_import':'TOWNSHIP__PRECINCT_IMPORT','district_type':'township','import_table':'electoral_district_t_import','dict_reader':True,'name_column':'vf_township','precinct_join_import_table':'electoral_district__precinct_t_import'},
                {'district_import':'WARD_IMPORT','district_precinct_import':'WARD__PRECINCT_IMPORT','district_type':'ward','import_table':'electoral_district_w_import','dict_reader':True,'name_column':'vf_ward','precinct_join_import_table':'electoral_district__precinct_w_import'},
                {'district_import':'CITY_COUNCIL_IMPORT','district_precinct_import':'CITY_COUNCIL__PRECINCT_IMPORT','district_type':'city_council','import_table':'electoral_district_cico_import','dict_reader':True,'name_column':'vf_city_council','precinct_join_import_table':'electoral_district__precinct_cico_import'},
                {'district_import':'MUNICIPAL_DISTRICT_IMPORT','district_precinct_import':'MUNICIPAL_DISTRICT__PRECINCT_IMPORT','district_type':'municipal_district','import_table':'electoral_district_muni_import','dict_reader':True,'name_column':'vf_municipal_district','precinct_join_import_table':'electoral_district__precinct_muni_import'},
            )

DEFAULT_VOTER_FILE_DISTRICTS = (
        'state',
        'county',
        'county_council',
        #'city_council',
        #'municipal_district',
        'school_district',
        'judicial_district',
        'congressional_district',
        'state_rep_district',
        'state_senate_district',
        #'township',
        #'ward'
        )

class TargetSmartTemplate():
    def __init__(self,election_key,state_key,voter_file_location,source_prefix=None,ed_defs=(),voter_file_districts=None,table_group=None):
        self.tdt = td.TableDefaultTemplate(election_key,state_key,source_prefix,voter_file_location=voter_file_location)
        self.VOTER_FILE_LOCATION = voter_file_location
        self.VOTER_FILE_DISTRICTS = voter_file_districts or DEFAULT_VOTER_FILE_DISTRICTS
        self.ed_defs = ed_defs + tuple(ed_def for ed_def in DEFAULT_ED_DEFS if ed_def['district_type'] in self.VOTER_FILE_DISTRICTS)

        """
        self.TABLE_GROUP = table_group or {
                'default':self.tdt.DEFAULT_VF_TABLE,
                'tables':
                (
                PRECINCT_ACTUAL,
                LOCALITY_ACTUAL,
                CONGRESSIONAL_DISTRICT_ACTUAL,
                STATE_REP_DISTRICT_ACTUAL,
                JUDICIAL_DISTRICT_ACTUAL,
                SCHOOL_DISTRICT_ACTUAL,
                COUNTY_COUNCIL_ACTUAL,
                COUNTY_ACTUAL,
                STATE_SENATE_DISTRICT_ACTUAL,
                CONGRESSIONAL_DISTRICT__PRECINCT_ACTUAL,
                STATE_REP_DISTRICT__PRECINCT_ACTUAL,
                JUDICIAL_DISTRICT__PRECINCT_ACTUAL,
                SCHOOL_DISTRICT__PRECINCT_ACTUAL,
                COUNTY_COUNCIL__PRECINCT_ACTUAL,
                COUNTY__PRECINCT_ACTUAL,
                STATE_SENATE_DISTRICT__PRECINCT_ACTUAL,
                )
                }
        """
        self.TABLES = {
            'PRECINCT_IMPORT':dict(self.tdt.default_vf_table().items() + {
                'udcs':dict(self.tdt.default_vf_table()['udcs'].items() + {'is_split':False}.items()),
                'table':'precinct_import',
                'dict_reader':True,
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'name':'vf_precinct_name',
                    'number':'vf_precinct_id',
                    'locality_id_long':'vf_county_name',
                    'identifier':{'function':concat_us,'columns':('vf_county_name','vf_precinct_name','vf_precinct_id')},
                    'id_long':{'function':concat_us,'columns':('vf_county_name','vf_precinct_name','vf_precinct_id')},
                    }
                }.items()
            ),

            'LOCALITY_IMPORT':dict(self.tdt.default_vf_table().items() + {
                'udcs':dict(self.tdt.default_vf_table()['udcs'].items() + {'type':'COUNTY'}.items()),
                'table':'locality_import',
                'dict_reader':True,
                'columns':{
                    'updated':{'function':nowtime,'columns':()},
                    'name':'vf_county_name',
                    'id_long':'vf_county_name',
                    'identifier':'vf_county_name',
                    }
                }.items()
            ),
        }

        for ed_def in self.ed_defs:
            self.TABLES[ed_def['district_import']]=self.electoral_district_import(**ed_def)
            self.TABLES[ed_def['district_precinct_import']]=self.electoral_district_precinct_import(**ed_def)


    def electoral_district_import(self, district_type,import_table,dict_reader,name_column,identifier=None,**kwargs):
        return dict(self.tdt.default_vf_table().items() + {
        'udcs':dict(self.tdt.default_vf_table()['udcs'].items() + {'type':district_type}.items()),
        'table':import_table,
        'dict_reader':dict_reader,
        'columns':{
            'updated':{'function':nowtime,'columns':()},
            'name':(name_column if type(name_column)==str else {'function':concat_us, 'columns':('vf_county_name','vf_county_council',)}),
            'identifier':identifier or {'function':ed_concat,'columns':((name_column,) if type(name_column)==str else name_column),'defaults':{'type':district_type}},
            'id_long':identifier or {'function':ed_concat,'columns':((name_column,) if type(name_column)==str else name_column),'defaults':{'type':district_type}},
            },
        }.items())

    def electoral_district_precinct_import(self, district_type,precinct_join_import_table,dict_reader,name_column,electoral_district_id=None,**kwargs):
        return dict(self.tdt.default_vf_table().items() + {
        'table':precinct_join_import_table,
        'dict_reader':dict_reader,
        'columns':{
            'electoral_district_id_long':electoral_district_id or {'function':ed_concat,'columns':((name_column,) if type(name_column)==str else name_column),'defaults':{'type':district_type}},
            'precinct_id_long':{'function':concat_us,'columns':('vf_county_name','vf_precinct_name','vf_precinct_id')},
            },
        }.items())

