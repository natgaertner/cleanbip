from collections import OrderedDict
ed_defs = (
        {'district_import':'APPEALS_COURT_IMPORT','district_precinct_import':'APPEALS_COURT__PRECINCT_IMPORT','district_type':'special_1_judicial_district','import_table':'electoral_district_special_1_import','dict_reader':True,'name_column':'special_1_judicial_district','precinct_join_import_table':'electoral_district__precinct_spcecial_1_import'},
        {'district_import':'DISTRICT_COURT_IMPORT','district_precinct_import':'DISTRICT_COURT__PRECINCT_IMPORT','district_type':'special_2_judicial_district','import_table':'electoral_district_special_2_import','dict_reader':True,'name_column':'special_2_judicial_district','precinct_join_import_table':'electoral_district__precinct_spcecial_2_import'},
        {'district_import':'JUSTICE_PEACE_COURT_IMPORT','district_precinct_import':'JUSTICE_PEACE_COURT__PRECINCT_IMPORT','district_type':'special_3_judicial_district','import_table':'electoral_district_special_3_import','dict_reader':True,'name_column':'special_3_judicial_district','precinct_join_import_table':'electoral_district__precinct_spcecial_3_import'},
        {'district_import':'POLICE_JURY_IMPORT','district_precinct_import':'POLICE_JURY__PRECINCT_IMPORT','district_type':'special_4_county_council','import_table':'electoral_district_special_4_import','dict_reader':True,'name_column':('county_id','special_4_county_council'),'precinct_join_import_table':'electoral_district__precinct_spcecial_4_import'},
    )
EXTRA_DISTRICTS = OrderedDict({
        'special_1_judicial_district':{'filename':'LA1202_AppealsCourt_20121004.txt','column':2},
        'special_2_judicial_district':{'filename':'LA1202_AppealsCourt_20121004.txt','column':3},
        'special_3_judicial_district':{'filename':'LA1202_AppealsCourt_20121004.txt','column':4},
        'special_4_county_council':{'filename':'LA1202_AppealsCourt_20121004.txt','column':5},
        })
