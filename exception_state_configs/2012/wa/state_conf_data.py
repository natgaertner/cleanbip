VOTER_FILE_DISTRICTS = (
'state',
'county_id',
#'county_council',
#'city_council',
#'municipal_district',
'school_district',
'judicial_district',
'congressional_district',
#'state_rep_district',
#'state_senate_district',
'township',
#'ward'
)
ed_defs = (
        {'district_import':'LEGISLATIVE_DISTRICT_IMPORT','district_precinct_import':'LEGISLATIVE_DISTRICT__PRECINCT_IMPORT','district_type':'legislative_district','import_table':'electoral_district_ld_import','dict_reader':True,'name_column':'vf_HD','precinct_join_import_table':'electoral_district__precinct_ld_import'},
        {'district_import':'COUNTY_COUNCIL_IMPORT','district_precinct_import':'COUNTY_COUNCIL__PRECINCT_IMPORT','district_type':'county_council','import_table':'electoral_district_cc_import','dict_reader':True,'name_column':'vf_county_council','precinct_join_import_table':'electoral_district__precinct_cc_import'},
        )
