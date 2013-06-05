from collections import OrderedDict
ed_defs = (
        {'district_import':'APPEALS_COURT_IMPORT','district_precinct_import':'APPEALS_COURT__PRECINCT_IMPORT','district_type':'special_1_judicial_district','import_table':'electoral_district_special_1_import','dict_reader':True,'name_column':'special_1_judicial_district','precinct_join_import_table':'electoral_district__precinct_spcecial_1_import'},
        {'district_import':'DISTRICT_COURT_IMPORT','district_precinct_import':'DISTRICT_COURT__PRECINCT_IMPORT','district_type':'special_2_judicial_district','import_table':'electoral_district_special_2_import','dict_reader':True,'name_column':'special_2_judicial_district','precinct_join_import_table':'electoral_district__precinct_spcecial_2_import'},
        {'district_import':'JUSTICE_PEACE_IMPORT','district_precinct_import':'JUSTICE_PEACE__PRECINCT_IMPORT','district_type':'special_3_county_council','import_table':'electoral_district_special_3_import','dict_reader':True,'name_column':('county_id','special_3_county_council'),'precinct_join_import_table':'electoral_district__precinct_spcecial_3_import'},
        {'district_import':'SCHOOL_NAME_IMPORT','district_precinct_import':'SCHOOL_NAME__PRECINCT_IMPORT','district_type':'special_4_school_district','import_table':'electoral_district_special_4_import','dict_reader':True,'name_column':'special_4_school_district','precinct_join_import_table':'electoral_district__precinct_spcecial_4_import'},
        )

EXTRA_DISTRICTS = OrderedDict({
        'special_1_judicial_district':{'filename':'20121018_AR_CourtofAppeals.txt','column':2,
        'special_2_judicial_district':{'filename':'20121018_AR_CourtofAppeals.txt','column':3},
        'special_3_county_council':{'filename':'20121018_AR_CourtofAppeals.txt','column':4},
        'special_4_school_district':{'filename':'20121019_AR_SchoolNames.txt','column':2},
        })


