from dashboard.models import Host, ConfiguredDataCenters
from . import services

import operator
import time


def update_hosts_flexibility(master, sub_id, floor, rack, host):
    
    host = Host.objects.filter(masterip=master).filter(sub_id = sub_id).filter(
        floorid=floor).filter(rackid=rack).filter(hostid=host)
    opposite = host.values().get()['flexible']
    print(not opposite)
    if not host.exists(): return Host.DoesNotExist
    try:
        host.update(flexible=not opposite)
    except: return


def get_hosts_flexibility(master, sub_id, floor, rack, host):
    
    host = Host.objects.filter(masterip=master).filter(sub_id = sub_id).filter(
        floorid=floor).filter(rackid=rack).filter(hostid=host)
    if not host.exists(): return Host.DoesNotExist
    try:
        host.values().get()['flexible']
    except: return


def get_all_hosts_power(master, sub_id):
    try: 
        startTime, endTime = services.get_start_end()
    except: return ConfiguredDataCenters.DoesNotExist
    for host in Host.objects.filter(sub_id=sub_id).filter(masterip=master).all().values():
        get_host_power(host['masterip'],host['sub_id'],host['datacenterid'],host['floorid'], host['rackid'],host['hostid'],startTime,endTime)


def get_host_power(master, sub_id, datacenter, floorid, rackid, hostid, startTime, endTime):

    host = Host.objects.filter(masterip=master).filter(sub_id = sub_id).filter(
        floorid=floorid).filter(rackid=rackid).filter(hostid=hostid)
    s = time.process_time()
    url = services.power_url(master, datacenter, str(floorid), str(rackid), str(hostid), startTime, endTime)
    response = services.get_response(url)
    data = response.json()
    
    if data != None: 
        total_watts = 0
        minutes = 0
        if isinstance(data['power'], list):
            lastTime = data['power'][-1]['timeStamp']
            for power in data['power']:
                total_watts += float(power['power'])
                minutes+=1
        else:
            lastTime = data['power']['timeStamp']
            minutes = 1 
            total_watts = float(data['power']['power'])

        hours = minutes/60
        kWh = total_watts/hours/1000
        
        pue = services.get_pue()
        carbon_conversion = services.get_carbon_conversion()
        energy_cost = services.get_energy_cost()

        cost__high = services.get_high_cost_tariff()
        cost__low = services.get_low_cost_tariff()

        carbon__high = services.get_high_carbon_tariff()
        carbon__low = services.get_low_carbon_tariff()

        kWh_consumed = total_watts/1000
        carbon_footprint = kWh_consumed * carbon_conversion
        carbon_footprint_low=kWh_consumed * carbon__low
        carbon_footprint_high=kWh_consumed * carbon__high
        
        cost_energy = kWh_consumed * energy_cost * pue
        cost_energy_low=kWh_consumed * cost__low * pue
        cost_energy_high=kWh_consumed * cost__high * pue

        cost_saving = cost_energy_high - cost_energy_low
        carbon_saving = carbon_footprint_high - carbon_footprint_low
        
        
        host.update(
                power_responses=minutes,
                kWh_consumed=kWh_consumed,
                power_last_response=lastTime,
                total_watt_hour=total_watts,
                cost_energy=cost_energy,
                cost_energy_low=cost_energy_low,
                cost_energy_high=cost_energy_high,
                carbon_footprint=carbon_footprint,
                carbon_footprint_high=carbon_footprint_high,
                carbon_footprint_low=carbon_footprint_low,
                cost_saving=cost_saving,
                carbon_saving=carbon_saving
        )
    

def get_total_power(master, sub_id):
    try: 
        startTime, endTime = services.get_start_end()
    except: return ConfiguredDataCenters.DoesNotExist
    for host in Host.objects.filter(sub_id=sub_id).filter(masterip=master).all().values():
        get_host_power(host['masterip'],host['sub_id'],host['datacenterid'],host['floorid'],
                       host['rackid'],host['hostid'],startTime,endTime)
