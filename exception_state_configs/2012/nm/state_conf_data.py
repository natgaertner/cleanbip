from collections import OrderedDict
ed_defs = (
        {'district_import':'EDUCATION_COMMISSION_IMPORT','district_precinct_import':'EDUCATION_COMMISSION__PRECINCT_IMPORT','district_type':'special_1_school_district','import_table':'electoral_district_special_1_import','dict_reader':True,'name_column':'special_1_school_district','precinct_join_import_table':'electoral_district__precinct_special_1_import'},
        )
EXTRA_DISTRICTS = OrderedDict({
        'special_1_school_district':{'filename':'20121022_NM_EducationCommission.txt','column':2},
        })
