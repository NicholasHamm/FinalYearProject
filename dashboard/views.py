#!/usr/bin/env python

from django.shortcuts import render
from dashboard.models import ConfiguredDataCenters, Floor, Rack, Host, Analysis, AvailableDatacenters, Application
from .services import services, asset_services, model_services, tagServices, analysisService
from . import forms
from django.views.decorators.csrf import csrf_protect
from datetime import datetime 
import time

# Code adapted and edited from:
# author = Daniel Houlihan
# version = 1.0.1
# source = https://csgitlab.ucd.ie/danielhoulihan/fyp_datacenter_management

################################################

__author__ = "Nicholas Hamm"
__studentnumber__ = "19439854"
__version__ = "1.0.1"
__email__ = "nicholas.hamm@ucdconnect.ie"
__status__ = "Production"

@csrf_protect
def loadDC(request):
    """ Home Tab
    From AvailableDatacenters, ConfiguredDatacenters collects the relevent information
    and sends to the HTML templates for the Home tab.
    
    POST methods:
    'to_delete' - remove selected datacenter from database
    'ip' - change the ip address of te master
    'to_configure' - setting up a new configured datacenter
    'current_datacenter' - select a current datacenter from the configured
    'update' - updates the selected datacenter
    """
    context = {}
        
    master = services.get_master()
    services.check_master()
    if request.method == 'POST':
        if 'to_delete' in request.POST:
            form = forms.DeleteConfigurationForm(request.POST)
            if form.is_valid():
                to_delete = form.cleaned_data['to_delete']
                ConfiguredDataCenters.objects.filter(sub_id=to_delete).filter(masterip=master).delete()
                Application.objects.filter(current=to_delete).filter(masterip=master).update(current=None)
                Host.objects.filter(sub_id=to_delete).filter(masterip=master).delete()
                Analysis.objects.filter(sub_id=to_delete).filter(masterip=master).delete()

    if request.method == 'POST':            
        if 'ip' in request.POST:
            form = forms.ChangeIPForm(request.POST)
            if form.is_valid():
                ip = form.cleaned_data
                Application.objects.update(masterip=ip, current=None)
                asset_services.get_available_datacenters()
                

    if request.method == 'POST':
        if 'to_configure' in request.POST:
            form = forms.ConfigureNewDatacenterForm(request.POST)
            if form.is_valid():
                to_configure, start, end, pue = form.cleaned_data
                services.increment_count()

                carbon_conversion = services.get_carbon_conversion()
                energy_cost = services.get_energy_cost()

                instance = str(to_configure)+"-"+str(Application.objects.all().values().get()['configured'])
                model_services.create_configured(master,
                instance,to_configure,start,end,pue,energy_cost,carbon_conversion)

                services.create_or_update_current(master,instance)
                asset_services.find_available_hosts(master, to_configure, instance)
                asset_services.get_hosts_energy(master, instance)
                tagServices.get_all_hosts_power(master, instance)
                analysisService.get_hosts_analysis(master, instance) 

            context['error'] = form

    if request.method == 'POST':
        if 'current_datacenter' in request.POST:
            form = forms.SelectCurrentForm(request.POST)
            if form.is_valid():
                current = form.cleaned_data['current_datacenter']
                services.create_or_update_current(master,current)
            context['error'] = form

    if request.method == 'POST':
        if 'update' in request.POST:
            if services.get_current_datacenter()!=Application.DoesNotExist:
                form = forms.UpdateDatacenterForm(request.POST)
                if form.is_valid():
                    to_update = form.cleaned_data['update']
                    asset_services.find_available_hosts(master, services.get_current_datacenter(), to_update)
                    asset_services.update_hosts_energy(master,to_update)
                    analysisService.get_hosts_analysis(master, to_update)
                    tagServices.get_all_hosts_power(master,to_update)

    sub_id = services.get_current_sub_id()

    try:
        last_update = Host.objects.filter(masterip=master).filter(
            sub_id=sub_id).all().values()[0]['cpu_last_response']
        last_update = datetime.fromtimestamp(int(last_update)).strftime("%Y-%m-%d %H:%M")
    except: last_update='Never'
        
    status = asset_services.get_available_datacenters()
    master = services.get_master()
    context['last_update'] = last_update
    context['datacenters'] = AvailableDatacenters.objects.filter(masterip=master).all()
    context['datacenters_count'] = AvailableDatacenters.objects.filter(masterip=master).all().count()
    context['configured_count'] = ConfiguredDataCenters.objects.filter(masterip=master).all().count()
    context['configured'] = ConfiguredDataCenters.objects.filter(masterip=master).all()
    context['master'] = services.get_master()
    context['current'] = services.get_current_for_html()
    context['page'] = "home"
    
    context['online'] = "false"
    if status!=ConnectionRefusedError:
        context['online'] = 'true'

    return render (request, 'dashboard/loadDC.html', context)

def tags(request):
    """ Tags Tab
    Finds the available hosts in the chosen datacenter. 
    POST method allows user to change the flexibility of the hosts.
    """    

    context = {}
    master = services.get_master()

    if Application.objects.filter(masterip=master).values().all().get()['current']==None:
        return services.prompt_configuration(request,"tags")

    sub_id = services.get_current_sub_id()

    if request.method == 'POST':
        if 'change-flexible' in request.POST:
            form = forms.ChangeFlexibilityForm(request.POST)
            if form.is_valid():
                hostid,rackid,floorid = form.cleaned_data
                tagServices.update_hosts_flexibility(master, sub_id, floorid, rackid, hostid)
    
    if request.method == 'POST':         
        if 'tariff-carbon' in request.POST:
            form = forms.ChangeTariffForm(request.POST)
            if form.is_valid():
                low,high = form.cleaned_data
                Application.objects.update(carbon_tariff_low=low,carbon_tariff_high=high)
                print('power')
                tagServices.get_all_hosts_power(master, sub_id)
            context['error'] = form
    
    if request.method == 'POST':            
        if 'tariff-cost' in request.POST:
            form = forms.ChangeTariffForm(request.POST)
            if form.is_valid():
                low,high = form.cleaned_data
                Application.objects.update(cost_tariff_low=low,cost_tariff_high=high)
                tagServices.get_all_hosts_power(master, sub_id)
            context['error'] = form

    context['master'] = master
    context['floors'] = Floor.objects.filter(sub_id=sub_id).filter(masterip=master).all()
    context['floor_count'] = Floor.objects.filter(sub_id=sub_id).filter(masterip=master).all().count()
    context['rack_count'] = Rack.objects.filter(sub_id=sub_id).filter(masterip=master).all().count()
    context['host_count'] = Host.objects.filter(sub_id=services.get_current_sub_id()).filter(masterip=master).all().count()
    context['current'] = services.get_current_for_html()
    context["tariff"] = Application.objects.all().get()
    context['racks'] = Rack.objects.filter(sub_id=sub_id).filter(masterip=services.get_master()).all()
    context['hosts'] = Host.objects.filter(sub_id=services.get_current_sub_id()).filter(masterip=master).all()
    context['analysis'] = Analysis.objects.filter(masterip=master).filter(sub_id=sub_id).all()
    context['page'] = 'tags'

    status = asset_services.get_available_datacenters()
    context['online'] = "false"
    if status!=ConnectionRefusedError:
        context['online'] = 'true'
    
    return render (request, 'dashboard/tags.html', context )


def home(request):
        return render (request, 'dashboard/home.html' )

def analysis(request):
    """ Analysis Tab
    Collects graphs from Analysis objects to show in web application analysis tab.
    """

    context = {}
    master = services.get_master()
    current_sub = services.get_current_sub_id()

    if Application.objects.filter(masterip=master).values().all().get()['current']==None:
        return services.prompt_configuration(request, "analysis")

    if request.method == 'POST':
        if 'refresh' in request.POST:
            if services.get_current_datacenter()!=Application.DoesNotExist:
                form = forms.RefreshGraphsForm(request.POST)
                if form.is_valid():
                    refresh = form.cleaned_data['refresh']
                    asset_services.find_available_hosts(master, services.get_current_datacenter(), refresh)
                    analysisService.get_hosts_analysis(master, refresh)

    analysis = Analysis.objects.filter(masterip=master).filter(sub_id=current_sub).all().values().get()

    context['page'] = 'analysis'
    context['master'] = master
    context['current'] = services.get_current_for_html()
    context['carbon'] = analysis['carbon_graph']
    context['energy'] = analysis['energy_graph']
    context['cost'] = analysis['cost_graph']

    status = asset_services.get_available_datacenters()
    context['online'] = "false"
    if status!=ConnectionRefusedError:
        context['online'] = 'true'

    return render(request, 'dashboard/analysis.html', context)





