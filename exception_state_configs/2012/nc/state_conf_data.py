from collections import OrderedDict
ed_defs = (
        {'district_import':'SUPERIOR_COURT_IMPORT','district_precinct_import':'SUPERIOR_COURT__PRECINCT_IMPORT','district_type':'special_1_judicial_district','import_table':'electoral_district_special_1_import','dict_reader':True,'name_column':'special_1_judicial_district','precinct_join_import_table':'electoral_district__precinct_special_1_import'},
        )
EXTRA_DISTRICTS = OrderedDict({
        'special_1_judicial_district':{'filename':'NC1205_SuperiorCourt.txt','column':2,'prepend':()},
        })
