VOTER_FILE_DISTRICTS = (
'state',
'county_id',
'county_council',
'city_council',
'municipal_district',
'school_district',
'judicial_district',
'congressional_district',
'state_rep_district',
'state_senate_district',
'residential_city',
#'township',
#'ward'
)
ed_defs = (
        {'district_import':'CITY_IMPORT','district_precinct_import':'CITY__PRECINCT_IMPORT','district_type':'city','import_table':'electoral_district_ci_import','dict_reader':True,'name_column':'vf_reg_cass_city','precinct_join_import_table':'electoral_district__precinct_ci_import'},
        )
