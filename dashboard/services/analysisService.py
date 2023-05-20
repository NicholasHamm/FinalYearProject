from . import services
from dashboard.models import Host, Analysis, ConfiguredDataCenters
from collections import defaultdict
from functools import reduce

import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64
import numpy as np
from django.db.models.functions import TruncDay
from matplotlib.ticker import LinearLocator
import collections
import operator
import time
import pandas as pd
import io
import json

matplotlib.use('Agg')
plt.switch_backend('Agg') 

GRAPH_DIVIDE = 1000 #MegaWh to kWh
HIGH_TARIFF_START = 8
HIGH_TARIFF_END = 19

def get_hosts_analysis(master, sub_id):
    
    startTime, endTime = services.get_start_end()
    available_hosts = get_all_host_values(master,sub_id)
    analysis = get_analysis(master,sub_id)
    hostid = get_all_hostids(available_hosts)


    if analysis.exists():
        delete_analysis_data(master, sub_id)
        create_analysis(startTime, endTime, available_hosts)
    else:
        create_analysis(startTime, endTime, available_hosts)

    analysis = get_analysis_dict(master, sub_id)
    
    decoded_data = json.loads(analysis)
    df = pd.DataFrame(decoded_data)
    df = df.fillna(0)

    analysis = Analysis.objects.filter(masterip=master).filter(sub_id=sub_id).all()
    
    total_usage = df.drop(columns=["hour"]).to_numpy().sum() * ConfiguredDataCenters.objects.filter(
        masterip=master).filter(sub_id=sub_id).values().get()['carbon_conversion']
    total_hours = get_total_hours(startTime, endTime)
    analysis.update(
        carbon_graph = plot_usage(df,'kgC02', 'Carbon', hostid),
        energy_graph = plot_usage(df,'kWh', 'Energy', hostid),
        cost_graph = plot_usage(df,'€', 'Cost', hostid),
        total_usage = total_usage,
        total_hours = total_hours
    )


def create_analysis(startTime, endTime, available_hosts):
    df_list=[hour_range()]

    for host in available_hosts:
        s = time.process_time()
        url = services.power_url(host['masterip'],host['datacenterid'],str(host['floorid']),
                                    str(host['rackid']),str(host['hostid']),startTime,endTime)
        response = services.get_response(url)
        data = response.json()

        addHour=int(60*60)
        hourCount=int(0)
        start=int(startTime)

        energy = defaultdict(list)
        if data!=None: 
            if isinstance(data['power'],list):
                for power in data['power']:
                    if int(power['timeStamp']) > start & hourCount < 24:
                            energy[hourCount].append(float(power['power']))
                            hourCount+=1
                    if hourCount == 24:
                        hourCount = 0
            hourlyResult = {key: sum(values) for key, values in energy.items()}
            df = pd.DataFrame(hourlyResult.items(), columns=['hour', str(host['hostid'])])
            df[str(host['hostid'])] = df[str(host['hostid'])]/GRAPH_DIVIDE
            df_list.append(df)


    allHosts = reduce(lambda x, y: pd.merge(x, y, on = 'hour', how='left'), df_list)
    allHosts = allHosts.fillna(0)
    # allHosts['Total'] = allHosts[allHosts.columns[1:]].sum(axis=1)

    df_dicts = list(allHosts.T.to_dict().values())
    encoded_json = json.dumps(df_dicts) 

    Analysis.objects.get_or_create(
        masterip=services.get_master(),
        sub_id=services.get_current_sub_id,
        energy_dict=encoded_json
    )

def plot_usage(table, ylabel, graph, hosts):

    hour = table["hour"].apply(int).tolist()
    x = np.arange(len(hour))
    y = list(table.columns.values.tolist())
    dfy = table.drop(columns=["hour"])

    if graph == 'Energy':
        dfy = dfy
    if graph == 'Carbon':
        dfy = carbon_usage(dfy)
    if graph == 'Cost':
        dfy = cost_estimate(dfy)

    y_max = 0
    for host in hosts:
        if host in dfy.columns:
            exists = dfy[host].max()
            if exists > y_max:
                y_max = exists
    y_lim = float(y_max + (y_max*0.25))

    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)

    for attribute, measurement in dfy.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        # ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_xlabel('(24 Hour Format)')
    ax.set_title(graph + ' Graph')
    ax.set_xticks(x + width, hour)
    ax.legend(loc='upper right', ncols=len(x), title="Host ID:", fontsize='medium', fancybox=True)
    ax.set_ylim(0, y_lim)

    # add bg colour
    ax.axvspan(HIGH_TARIFF_START, HIGH_TARIFF_END, facecolor='red',  alpha=0.2, ymin=0, ymax=1)
    ax.axvspan(0, HIGH_TARIFF_START, facecolor='green',  alpha=0.2, ymin=0, ymax=1)
    ax.axvspan(HIGH_TARIFF_END, 23, facecolor='green',  alpha=0.2, ymin=0, ymax=1)

    # add label
    ax.text(HIGH_TARIFF_START/2, y_lim-(y_lim*.15), 'Off-peak', ha='center', va='center', fontsize=14, alpha=0.5)
    ax.text(23 - (23-HIGH_TARIFF_END)/2, y_lim-(y_lim*.15), 'Off-peak', ha='center', va='center', fontsize=14, alpha=0.5)
    ax.text(HIGH_TARIFF_END - (HIGH_TARIFF_END-HIGH_TARIFF_START)/2, y_lim-(y_lim*.15), 'High-demand', ha='center', va='center', fontsize=18, alpha=0.5)

    # convert to bytes for storing
    flike = io.BytesIO()
    fig.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    matplotlib.pyplot.close()
    return b64

def carbon_usage(table):
    try:
        temp = table.copy()
    except: return

    carbon = services.get_carbon_conversion()
    high = services.get_high_carbon_tariff()
    low = services.get_low_carbon_tariff()

    for col in temp.columns:
        for row in temp.index:
            if row < HIGH_TARIFF_START or row > HIGH_TARIFF_END:
                mult = low * carbon
            else:
                mult = high * carbon
            temp.at[row, col] = temp.at[row, col] * mult
            
    return temp

def cost_estimate(table):
    try:
        temp = table.copy()
    except: return

    cost = services.get_energy_cost()
    high = services.get_high_cost_tariff()
    low = services.get_low_cost_tariff()

    for col in temp.columns:
        for row in temp.index:
            if row < HIGH_TARIFF_START or row > HIGH_TARIFF_END:
                mult = low * cost
            else:
                mult = high * cost
            temp.at[row, col] = temp.at[row, col] * mult

    return temp

def unix_range(startTime,endTime):
    start = int(startTime)
    addHour = int(60*60)
    range1 = int((int(endTime)-start)/addHour)
    hours=[]
    for i in range(0,range1+1):
        hours.append(start)
        start+=addHour
    base_df = pd.DataFrame(hours, columns=['hour'])
    return base_df

def hour_range():
    start = 0
    range1 = int(int(23)-0)
    hours=[]
    for i in range(0,range1+1):
        hours.append(start)
        start+=1
    base_df = pd.DataFrame(hours, columns=['hour'])
    return base_df


def get_analysis(master,sub_id):
    try:
        return Analysis.objects.filter(masterip=master).filter(sub_id=sub_id).all()
    except: return Analysis.DoesNotExist


def get_all_host_values(master, sub_id):
    try:
        return Host.objects.filter(masterip=master).filter(sub_id=sub_id).all().values()
    except: return Host.DoesNotExist

    
def get_analysis_dict(master, sub_id):
    try:
        return Analysis.objects.filter(masterip=master).filter(
            sub_id=sub_id).all().values().get()['energy_dict']
    except: return Analysis.DoesNotExist


def get_total_hours(startTime, endTime):
    total = (float(endTime)-float(startTime))
    return total/(60*60)


def delete_analysis_data(master,sub_id):
    try:
        return Analysis.objects.filter(masterip=master).filter(sub_id=sub_id).delete()
    except: return Analysis.DoesNotExist


def get_all_hostids(available_hosts):
    try:
        hosts = []
        for host in available_hosts:
            h_id = str(host['hostid'])
            hosts.append(h_id)
        return hosts
    except: Analysis.DoesNotExist


