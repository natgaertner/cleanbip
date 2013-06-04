import table_defaults as td

class TargetSmartManipulationDataTemplate():
    def __init__(self,table_import_data,electoral_district_union=None,electoral_district_precinct_union=None):
        self.table_import_data=table_import_data
        self.tdt = table_import_data.tdt

        self.TABLES = {
            'PRECINCT_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'precinct',
                'import_table':table_import_data.TABLES['PRECINCT_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},{'long':'locality_id_long','real':'locality_id'}),
                'distinct_on':('id_long',),
                'long_from':('id_long',),
                'long_to':(
                    {
                        'to_table':'locality_import',
                        'local_key':'locality_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id',
                    },
                    )
                }.items()
            ),

            'LOCALITY_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'locality',
                'import_table':table_import_data.TABLES['LOCALITY_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},),
                'distinct_on':('id_long',),
                'long_from':('id_long',),
                }.items()
            ),
        }

        for ed_def in table_import_data.ed_defs:
            self.TABLES[ed_def['district_import'].replace('IMPORT','ACTUAL')]=self.electoral_district_actual(ed_def['import_table'])
            self.TABLES[ed_def['district_precinct_import'].replace('IMPORT','ACTUAL')]=self.electoral_district_precinct_actual(ed_def['precinct_join_import_table'])

        self.UNIONS = {
            'ELECTORAL_DISTRICT_UNION':electoral_district_union or {
                'actual_table':self.electoral_district_actual('electoral_district_import'),
                'components':[ed_def['import_table'] for ed_def in table_import_data.ed_defs],
                },

            'ELECTORAL_DISTRICT__PRECINCT_UNION':electoral_district_precinct_union or {
                'actual_table':self.electoral_district_precinct_actual('electoral_district__precinct_import'),
                'components':[ed_def['precinct_join_import_table'] for ed_def in table_import_data.ed_defs],
                },
        }

    def electoral_district_actual(self,import_table):
        return dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
            'schema_table':'electoral_district',
            'import_table':import_table,
            'long_fields':({'long':'id_long','real':'id'},),
            'long_from':('id_long',),
            'distinct_on':('id_long',),
            }.items())

    def electoral_district_precinct_actual(self,import_table):
        return dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
            'schema_table':'electoral_district__precinct',
            'import_table':import_table,
            'long_fields':({'long':'electoral_district_id_long','real':'electoral_district_id'},{'long':'precinct_id_long','real':'precinct_id'},),
            'distinct_on':('precinct_id_long','electoral_district_id_long',),
            'long_to':(
                {
                    'to_table':'electoral_district_import',
                    'local_key':'electoral_district_id_long',
                    'to_key':'id_long',
                    'real_to_key':'id',
                    },
                {
                    'to_table':'precinct_import',
                    'local_key':'precinct_id_long',
                    'to_key':'id_long',
                    'real_to_key':'id',
                    },
                ),
            }.items())
