from django.test import TestCase
from django.core.management import call_command

from ppts.models import Record
from ppts.models import DwellingType
from ppts.models import LandUse
from ppts.models import Location
from ppts.models import Planner
from ppts.models import ProjectFeature
from ppts.models import ProjectDescription
from ppts.models import Record
from ppts.models import RecordType

class DataImportTests(TestCase):
    
    TEST_DATA = '../sf-planning-pipeline/planning-department-records-2018/PPTS_Records_data.csv'
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('loadppts', cls.TEST_DATA, '--quicktest')
    
    def test_tables_exist(self):
        '''Tables successfully created'''
        self.assertTrue(DwellingType.objects.count() > 0)
        self.assertTrue(LandUse.objects.count() > 0)
        self.assertTrue(Location.objects.count() > 0)
        self.assertTrue(Planner.objects.count() > 0)
        self.assertTrue(ProjectFeature.objects.count() > 0)
        self.assertTrue(ProjectDescription.objects.count() > 0)
        self.assertTrue(Record.objects.count() > 0)
        self.assertTrue(RecordType.objects.count() > 0)
        self.assertTrue(Record.project_description.through.objects.count() > 0)
        self.assertTrue(Record.parent.through.objects.count() > 0)
        
    def test_records_given_location(self):
        '''Record objects are successfully assigned a non-null location'''
        record = Record.objects.get(pk=1)
        self.assertTrue(record.location,'Records have not been associated with locations')
        
    def test_record_type_acronyms(self):
        '''Record_type successfully cleaned to list 3-letter acronyms'''
        for record_type in RecordType.objects.iterator():
            category = record_type.category
            self.assertTrue((category.lower() == 'other') or 
                            (len(category) == 3 and category.isupper() and category.isalpha()),
                           "Record type %s not cleaned" % category)
            
    def test_project_feature_addition(self):
        '''Net change in units of project features equals proposed units minus existing units'''
        for feature in ProjectFeature.objects.iterator():
            self.assertTrue(feature.net == feature.proposed - feature.exist,"Units don't add up for %s" % feature.type)
    