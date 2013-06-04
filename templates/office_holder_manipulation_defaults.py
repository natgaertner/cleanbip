import table_defaults as td

class OfficeHolderManipulationDataTemplate():
    def __init__(self,table_import_data):
        self.table_import_data=table_import_data
        self.tdt = table_import_data.tdt
        self.UNIONS = {}

        self.TABLES = {
            'OFFICE_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'office',
                'import_table':self.table_import_data.TABLES['OFFICE_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},{'long':'electoral_district_id_long','real':'electoral_district_id'}),
                'distinct_on':('id_long',),
                'long_from':('id_long',),
                'long_to':(
                    {
                        'to_table':'electoral_district_import',
                        'local_key':'electoral_district_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id',
                        },
                    ),
                }.items()
            ),

            'OFFICE_HOLDER_TO_OFFICE_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'office_holder_to_office',
                'import_table':self.table_import_data.TABLES['OFFICE_HOLDER_TO_OFFICE_IMPORT']['table'],
                'long_fields':({'long':'office_holder_id_long','real':'office_holder_id'},{'long':'office_id_long','real':'office_id'}),
                'long_to':(
                    {
                        'to_table':'office_holder_import',
                        'local_key':'office_holder_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id'
                        },
                    {
                        'to_table':'office_import',
                        'local_key':'office_id_long',
                        'to_key':'id_long',
                        'real_to_key':'id'
                        }
                    )
                }.items()
            ),

            'OFFICE_HOLDER_ACTUAL':dict(self.tdt.DEFAULT_ACTUAL_TABLE.items() + {
                'schema_table':'office_holder',
                'import_table':self.table_import_data.TABLES['OFFICE_HOLDER_IMPORT']['table'],
                'long_fields':({'long':'id_long','real':'id'},),
                'long_from':('id_long',),
                }.items()
            ),
        }

