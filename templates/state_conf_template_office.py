import os, imp
import target_smart_defaults as tsd
import target_smart_manipulation_defaults as tsmd
import office_holder_defaults as ohd
import office_holder_manipulation_defaults as ohmd

class StateConfTemplate():
    def __init__(self,unit,ed_defs=(),EXTRA_DISTRICTS=None,COUNTY_SCHOOL_DISTRICT=False,COUNTY_JUDICIAL_DISTRICT=False,ed_map_wrapper=None,VOTER_FILE_DISTRICTS=None):
        self.COUNTY_SCHOOL_DISTRICT = COUNTY_SCHOOL_DISTRICT
        self.COUNTY_JUDICIAL_DISTRICT = COUNTY_JUDICIAL_DISTRICT
        self.tst = tsd.TargetSmartTemplate(unit.election_key,unit.state_key,os.path.join(unit.__path__[0],'vf_compressed'),'_'.join(unit.partition_suffixes))
        self.ed_map_template = unit.ed_map.EdMapTemplate(unit.districts,self.COUNTY_SCHOOL_DISTRICT,self.COUNTY_JUDICIAL_DISTRICT)
        if ed_map_wrapper:
            self.ed_map=ed_map_wrapper(self.ed_map_template.ed_map)
        else:
            self.ed_map=self.ed_map_template.ed_map
        self.oht = ohd.OfficeHolderTemplate(unit.election_key,unit.state_key,os.path.join(unit.__path__[0],'office_holders'),self.ed_map,'_'.join(unit.partition_suffixes))
        self.tsmdt = tsmd.TargetSmartManipulationDataTemplate(self.tst)
        self.ohmdt = ohmd.OfficeHolderManipulationDataTemplate(self.oht)
        self.IMPORT_TABLES = self.tst.TABLES.values()+self.oht.TABLES.values()
        self.ACTUAL_TABLES = self.tsmdt.TABLES.values()+self.ohmdt.TABLES.values()
        self.UNIONS = self.tsmdt.UNIONS.values()+self.ohmdt.UNIONS.values()

        self.UNCOMPRESSED_VOTER_FILE_LOCATION = os.path.join(unit.__path__[0],'voterfile.txt')
        self.UNCOMPRESSED_VOTER_FILE_ZIP_LOCATION = os.path.join(unit.__path__[0],'voterfile.zip')
        self.VOTER_FILE_DISTRICTS = VOTER_FILE_DISTRICTS or self.tst.VOTER_FILE_DISTRICTS
        self.EXTRA_DISTRICTS = EXTRA_DISTRICTS
