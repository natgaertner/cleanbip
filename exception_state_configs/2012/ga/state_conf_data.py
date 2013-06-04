state_specific.COUNTY_SCHOOL_DISTRICT = True
COUNTY_SCHOOL_DISTRICT = True
DEFAULT_VOTER_FILE_DISTRICTS = (
        'state',
        'county_id',
        'county_council',
        #'city_council',
        #'municipal_district',
        #'school_district',
        'judicial_district',
        'congressional_district',
        'state_rep_district',
        'state_senate_district',
        #'township',
        #'ward'
        )
ed_defs = (
        {'district_import':'SCHOOL_DISTRICT_IMPORT','district_precinct_import':'SCHOOL_DISTRICT__PRECINCT_IMPORT','district_type':'school_district','import_table':'electoral_district_schd_import','dict_reader':True,'name_column':('vf_county_name','vf_school_district'),'precinct_join_import_table':'electoral_district__precinct_schd_import'},
        {'district_import':'EDUCATION_COMMISSION_IMPORT','district_precinct_import':'EDUCATION_COMMISSION__PRECINCT_IMPORT','district_type':'special_1_school_district','import_table':'electoral_district_special_1_import','dict_reader':True,'name_column':'special_1_school_district','precinct_join_import_table':'electoral_district__precinct_special_1_import'},
        )
