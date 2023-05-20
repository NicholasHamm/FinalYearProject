from django.test import TestCase
from dashboard.services import tagServices, services
from dashboard.models import Host, ConfiguredDataCenters, Application
import datetime

class TagServicesTestEmpty(TestCase):
        
    def test_get_all_hosts_power_empty(self):
        exception = tagServices.get_all_hosts_power("master", "sub_id")
        self.assertEquals(exception, ConfiguredDataCenters.DoesNotExist)
        
    def test_total_power_empty(self):
        exception = tagServices.get_total_power("master", "sub_id")
        self.assertEquals(exception, ConfiguredDataCenters.DoesNotExist)
        
        
class TagServicesTest(TestCase):
    
    def setUp(self):
        
        ConfiguredDataCenters.objects.create(
            masterip = "master",
            sub_id = "sub_id",
            energy_cost=0.5,
            startTime = datetime.date(2022, 10, 19),
            endTime = datetime.date(2022, 10, 29),
            pue=1.5,
            carbon_conversion=0.4,
        )

        Host.objects.create(
            masterip = "master",
            sub_id = "sub_id",
            datacenterid = "datacenter",
            floorid = 1,
            rackid = 2,
            hostid = 3, 
            hostname = "name",
            hostdescription = "description",
            hostType = "type",
            processors = 2,
            ipaddress = "ip"
        )
        Application.objects.create(
            masterip="master",
            current="sub_id"
        )
        
    def test_get_flexibility(self):
        tagServices.get_hosts_flexibility("master", "sub_id",1,2,3)
        flex = Host.objects.all().values().get()['flexible']
        
        self.assertEquals(flex, False)

        
    def test_update_flexibility(self):
        tagServices.update_hosts_flexibility("master", "sub_id",1,2,3)
        flex = Host.objects.all().values().get()['flexible']
        
        self.assertEquals(flex, True)
        