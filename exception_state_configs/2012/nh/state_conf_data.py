VOTER_FILE_DISTRICTS = (
'state',
'county_id',
'county_council',
#'city_council',
#'municipal_district',
'school_district',
'judicial_district',
'congressional_district',
'state_rep_district',
'state_senate_district',
'township',
#'ward'
)
ed_defs = (
        {'district_import':'FLOATERIAL_IMPORT','district_precinct_import':'FLOATERIAL__PRECINCT_IMPORT','district_type':'special_1_state_rep_district','import_table':'electoral_district_special_1_import','dict_reader':True,'name_column':'special_1_state_rep_district','precinct_join_import_table':'electoral_district__precinct_special_1_import'},
        )
EXTRA_DISTRICTS = OrderedDict({
        'special_1_state_rep_district':{'filename':'20121022_NH_Floaterial.txt','column':2,'prepend':()},
        })
