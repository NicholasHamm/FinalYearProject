from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from dashboard.models import ConfiguredDataCenters, Application, Analysis
from dashboard.services import analysisService, services
import pandas as pd
import datetime

class AnalysisServicesTestEmpty(TestCase):

    def test_carbon_usage_empty(self):
        df = pd.DataFrame()
        new_table = analysisService.carbon_usage(df)
        self.assertEqual(True, new_table.equals(pd.DataFrame()))
        
    def test_carbon_usage_None(self):
        new_table = analysisService.carbon_usage(None)
        self.assertEqual(new_table,None)
        
    def test_cost_estimate_empty(self):
        df = pd.DataFrame()
        new_table = analysisService.cost_estimate(df)
        self.assertEqual(True, new_table.equals(pd.DataFrame()))
        
    def test_cost_estimate_None(self):
        new_table = analysisService.cost_estimate(None)
        self.assertEqual(new_table,None)
        
    def test_get_analsis_dict_none(self):
        exception = analysisService.get_analysis_dict("master", "current_sub")
        self.assertEquals(exception, Analysis.DoesNotExist)

    # def test_get_host_dict_none(self):
    #     exception = analysisService.get_hosts_analysis("master", "current_sub")
    #     self.assertEquals(exception, Analysis.DoesNotExist)
        
        
class AnalysisServicesTest(TestCase):
    
    def setUp(self):
        ConfiguredDataCenters.objects.create(
            masterip="master",
            sub_id='sub_id-1',
            datacenterid='sub_id',
            startTime=datetime.date(2021, 10, 19),
            endTime=datetime.date(2021, 10, 21),
            pue=1.5,
            energy_cost=0.3,
            carbon_conversion=0.8
            )

        Application.objects.create(
            masterip="master",
            current="sub_id-1"
        )
        
        Analysis.objects.create(
            masterip="master",
            sub_id = "sub_id-1",
            energy_dict = "dictionary"
        )
        
    # def test_unix_date(self):
    #     start, end = services.get_start_end()
    #     test = analysisService.unix_range(start,end)
    #     expected_dates = [1634601600, 1634688000, 1634774400]
    #     self.assertEqual(expected_dates,list(test['hour']))

    # def test_carbon_usage(self):
    #     df = pd.DataFrame({'day': [1634601600,1634688000], 'Total': [1000,2000]})
    #     new_table = analysisService.carbon_usage(df)
    #     self.assertEqual(True, new_table.equals(pd.DataFrame({'day': [1634601600,1634688000], 'Total': [800.0,1600.0]})))

    # def test_cost_estimate(self):
    #     df = pd.DataFrame({'day': [1634601600,1634688000], 'Total': [1000,2000]})
    #     new_table = analysisService.cost_estimate(df)
    #     self.assertEqual(True, new_table.equals(pd.DataFrame({'day': [1634601600,1634688000], 'Total': [300.0,600.0]})))
               
    def test_get_all_host_values(self):
        exception = analysisService.get_all_host_values("master", "current_sub")
        self.assertFalse(exception.exists())
        
    # def test_get_host_analysis(self):
    #     exception = analysisService.get_hosts_analysis("master", "sub_id-1")
    #     self.assertTrue(exception.exists())
        
    def test_get_energy_dict(self):
        dict = analysisService.get_analysis_dict("master", "sub_id-1")
        self.assertEquals(dict, "dictionary")