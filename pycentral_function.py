
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
from pprint import pprint
import json
import typer
import pwinput
import sys
from rich import print
from rich.console import Console

# Import Aruba Central Base
""" Define pycentral from folder-name"""
from pycentral import NewCentralBase
from pycentral.push_config import *
#from pycentral.base import ArubaCentralBase
from pycentral.aos10_gw import *
from pycentral.msp import *
from pycentral.configuration import *
from pycentral.monitoring import *
from pycentral.audit_logs import *
from pycentral.rapids import *
from pycentral.workflows.workflows_utils import *  # Get central_information from file by calling this module 
from pycentral.device_inventory import Inventory

# Create an instance of ArubaCentralBase using API access token
# or API Gateway credentials.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
central_data1= BASE_DIR +'/pycentral/central_data.yml'
#central_data1= BASE_DIR +'/pycentral-v2/cnx_data.yml'
account_name = "vorawut_sg"
#account_name = "aruba_cic"
#account_name = "singapore_seath"
central = get_conn_from_file(central_data1,account=account_name, logger=None)

"""
central_info = {
                    
      "base_url": "https://internal-apigw.central.arubanetworks.com",
      #"base_url": "https://apigw-apaceast.central.arubanetworks.com",
      "token" : {"access_token": "YEhbf3nyo4NlvkAtipXU0XPWswrTmezg"}
    }
ssl_verify = True
central = ArubaCentralBase(central_info=central_info,
                              ssl_verify=ssl_verify)


"""
ap_conf = ApConfiguration()
ap_setup = ApSettings()
audit = Audit()
console = Console()
devices = Devices()
gateway= AOS10()
group = Groups()
msp = MSP()
rapids = Rogues()
template= Templates()
template_var= Variables()
wlan = Wlan()



app = typer.Typer()

@app.command(help="show tenant ")
def show_tenants():
  module_resp = msp.get_tenant_info(central)
  for i in range (len(module_resp["msg"]["customers"])) :
    print("[bold blue]customer-id[/bold blue] {} " .format (module_resp["msg"]["customers"][i]["customer_id"]))
    print("[bold blue]customer-name[/bold blue] {}\n" .format (module_resp["msg"]["customers"][i]["customer_name"]))
  
@app.command(help="delete tenant ")
def delete_tenant(customer_id: str = typer.Argument(help="customer/tenant id")):
  module_resp = msp.delete_tenant(central,customer_id)
  pprint (module_resp)


@app.command(help="show AP neighbor under global level or specific group ")
def show_neighbor_aps(group_name: str = typer.Option(default="",help="show neighbor AP under this group")):
  module_resp = rapids.list_neighbor_aps(central,group_name)
  pprint(module_resp["msg"])

@app.command()
def show_interference_aps(group_name: str = typer.Option(default="",help="show neighbor AP under this group"),
                          ap_label:str = typer.Option(default="",help="show neighbor AP under this label")
                          ):
  print (ap_label)
  module_resp = rapids.list_interfering_aps(central,group_name,label=ap_label)
  pprint(module_resp["msg"])


@app.command()
def show_events_detail(event_id: str = typer.Option(help="use show-events to get event-id detail for more information")):
  module_resp = audit.get_eventlogs_detail(central,event_id)
  pprint(module_resp["msg"])

@app.command()
def show_events(limit: int = typer.Option(default=100), offset: int = typer.Option(default=0)):
  module_resp = audit.get_eventlogs(central,limit,offset)
  pprint(module_resp["msg"])

@app.command()
def show_group(offset: int = typer.Option(default=0),limit: int = typer.Option(default=20)):
  module_resp = group.get_groups(central,offset,limit)
  pprint(module_resp)

@app.command()
def clone_group(new_group, existing_group):
  module_resp = group.clone_create_group(central,new_group, existing_group)
  pprint(module_resp)


@app.command()
def create_group(config: str = typer.Argument(help="config file")):

  with open(config,'r') as config_file:
    group_config = json.load(config_file)

  #wlan_data = {}
  #wlan_data.update(ap_sn)
  #wlan_data['services']=[license_type]
  wlan_data = group_config
  apiPath = "/configuration/v3/groups"
  apiMethod = "POST" 
  apiData = wlan_data
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath,
                              apiData=apiData
                              )
  pprint(base_resp)


@app.command()
def delete_group(group_name):
  module_resp=group.delete_group(central,group_name)
  pprint(module_resp)

@app.command(help="Create the template configuration file")
def create_template(group_name,
                    template_name: str =typer.Argument(help="creating template name"),
                    config_file: str =typer.Argument(help="choose template config file, should be text file"),
                    device_type:str =typer.Argument(help="default is IAP but you have to choose --> ArubaSwitch, CX")
                    ):
  module_resp = template.create_template(central,group_name,template_name,config_file,device_type)
  pprint(module_resp)

@app.command(help="Update the template configuration file")
def update_template(group_name,
                    template_name: str =typer.Argument(help="template name"),
                    config_file: str =typer.Argument(help="choose template config file, should be text file"),
                    device_type:str =typer.Argument(help="default is IAP but you have to choose --> ArubaSwitch, CX")
                    ):
  module_resp = template.update_template(central,group_name,template_name,config_file,device_type)
  pprint(module_resp)


@app.command(help="Create and upload variable file")
def create_variable(config_file: str =typer.Argument(help="choose template variable file, JSON format ")):

  module_resp = template_var.create_template_variables_file(central,config_file,format='JSON')
  pprint(module_resp)


@app.command()
def create_new_wlan(group_name,
                    wlan_name: str =typer.Argument(help="WLAN profile name not SSID name "),
                    config_file: str =typer.Argument(help="use sample wlan_config.json ")
                    ):
  with open(config_file,'r') as config_file:
    wlan_config = json.load(config_file)

  module_resp = wlan.create_wlan(central,group_name,wlan_name,wlan_config)
  pprint(module_resp)

@app.command()
def delete_wlan(group_name,
                    wlan_name: str =typer.Argument(help="WLAN profile name not SSID name ")
                    ):
  module_resp = wlan.delete_wlan(central,group_name,wlan_name)
  pprint(module_resp)


@app.command(help="update basic wlan config ie. ESSID, policy firewall, BW control etc.")
def update_config_wlan(group_name,wlan_name,config_file: str =typer.Argument(help="use sample wlan_config.json ") ):
  with open(config_file,'r') as config_file:
    wlan_config = json.load(config_file)

  module_resp = wlan.update_wlan(central,group_name,wlan_name,wlan_config)
  pprint(module_resp)

@app.command(help="show ap setting individual by Serial number")
def show_ap_settings(ap_sn):
  module_resp = ap_setup.get_ap_settings(central,ap_sn)
  pprint(module_resp)

@app.command(help="Update individual AP ie hostname,ip-address etc.")
def update_ap_settings(ap_sn,config_file):
  with open(config_file,'r') as config_file:
    ap_data = json.load(config_file)

  module_resp = ap_setup.update_ap_settings(central,ap_sn,ap_data)
  pprint(module_resp)

@app.command(help="show All AP configuration from Group level")
def show_ap_config(group_name):
  module_resp = ap_conf.get_ap_config(central,group_name)
  module_resp = {"clis": module_resp["msg"] }
  save_file_name = input("save your configuration file .json ")

  with open(save_file_name, 'w') as file:
    file.write(json.dumps(module_resp,indent=2))
#  with open(r"whole_config.json", 'w') as file:
#   file.write(json.dumps(module_resp,indent=2))

@app.command(help="show All AP configuration from Group level in full")
def show_wlan_config_full(group_name,wlan_name):
  save_file_name = input("save your configuration file .json ")
  apiPath = "/configuration/full_wlan/"+group_name+"/"+wlan_name
  apiMethod = "GET"
  base_resp = central.command(apiMethod=apiMethod,
                               apiPath=apiPath)
  wlan_config = {"value":""}
  wlan_config["value"] = base_resp["msg"]

  with open(save_file_name, 'w') as file:
    file.write(json.dumps(wlan_config,indent=2))



@app.command(help="Replace All AP configuration from Group level")
def replace_ap_config(group_name,config_file):
  with open(config_file,'r') as config_file:
    ap_data = json.load(config_file)

  module_resp = ap_conf.replace_ap(central,group_name,ap_data)
  pprint(module_resp)

@app.command()
def change_wlan_status(group_name,wlan_name:str = typer.Argument(help="wlan profile name not SSID "),wlan_status:str = typer.Argument(help="enable or disable")):
  if wlan_status == "enable":
    wlan_status = True
  elif wlan_status == "disable":
    wlan_status = False
    
  module_resp = ap_conf.change_wlan_status(central,group_name,wlan_name,wlan_status)
  pprint(module_resp)

@app.command()
def move_device(group_name: str = typer.Argument(help="Group-name for devices to be moved"),
                devices_file: str = typer.Argument(help="serial number file in json format ")):
  with open(devices_file,'r') as config_file:
    sn_data = json.load(config_file)

  device_sn = sn_data["serials"]
  module_resp = devices.move_devices(central,group_name,device_sn)
  pprint(module_resp)

@app.command()
#def delete_device(ap_sn: str = typer.Argument(help="AP serial number ")):
def delete_device(config_file: str = typer.Argument(help="AP serial numner file in json format ")):
  with open(config_file,'r') as config_file:
    ap_sn = json.load(config_file)

  for i in range (len(ap_sn["serials"])) :
    #print (ap_sn["serial"][i])
    apiPath = "/monitoring/v1/aps/"+ap_sn["serials"][i]
    apiMethod = "DELETE"
    base_resp = central.command(apiMethod=apiMethod,
                               apiPath=apiPath)
    pprint(base_resp)

@app.command()
def show_list_aps():
  apiPath = "/monitoring/v2/aps"
  apiMethod = "GET"
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath)
  pprint(base_resp["msg"])

@app.command(help="show ap information detail by Serial number")
def show_ap_detail(ap_sn: str = typer.Argument(help="AP serial number ")):
  apiPath = "/monitoring/v1/aps/"+ ap_sn
  apiMethod = "GET"
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath)
  pprint(base_resp["msg"])



@app.command()
def update_11g_radio(group_name,dot11g_profile,config_file: str = typer.Argument(help="configuration file in json format ")):
  with open(config_file,'r') as config_file:
    wlan_data = json.load(config_file)
  
  apiPath = "/configuration/v1/dot11g_radio_profile/"+group_name+"/"+dot11g_profile  
  apiMethod = "POST" 
  apiData = wlan_data
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath,
                              apiData=apiData
                              )
  pprint(base_resp)

@app.command()
def update_11a_radio(group_name,dot11a_profile,config_file: str = typer.Argument(help="configuration file in json format ")):
  with open(config_file,'r') as config_file:
    wlan_data = json.load(config_file)

  apiPath = "/configuration/v1/dot11a_radio_profile/"+group_name+"/"+dot11a_profile  
  apiMethod = "POST" 
  apiData = wlan_data
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath,
                              apiData=apiData
                              )
  pprint(base_resp)

@app.command()
def assign_license(license_type: str = typer.Argument(help="type of license ie: foundation_ap"),
                   device_sn: str = typer.Argument(help=" ap serial in json format ap_sn.json ")):

  with open(device_sn,'r') as config_file:
    ap_sn = json.load(config_file)
  
  wlan_data = {}
  wlan_data.update(ap_sn)
  wlan_data['services']=[license_type]

  apiPath = "/platform/licensing/v1/subscriptions/assign"  
  apiMethod = "POST" 
  apiData = wlan_data
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath,
                              apiData=apiData
                              )
  pprint(base_resp)

@app.command()
def unassign_license(license_type: str = typer.Argument(help="type of license ie: foundation_ap"),
                   device_sn: str = typer.Argument(help=" ap serial in json format ap_sn.json ")):

  with open(device_sn,'r') as config_file:
    ap_sn = json.load(config_file)

  wlan_data = {}
  wlan_data.update(ap_sn)
  wlan_data['services']=[license_type]

  apiPath = "/platform/licensing/v1/subscriptions/unassign"
  apiMethod = "POST" 
  apiData = wlan_data
  base_resp = central.command(apiMethod=apiMethod,
                              apiPath=apiPath,
                              apiData=apiData
                              )
  pprint(base_resp)




@app.command(help="show gateway commited configuration and save to file gw_config.json")
def show_gw_committed(group_name):
  resp = gateway.get_config_committed(central,group_name)
  resp = {"cli_cmds": resp["msg"]["config"]}
  save_file_name = input("save your configuration file .json ")

  with open(save_file_name, 'w') as file:
      file.write(json.dumps(resp,indent=2))
  pprint(resp)


@app.command(help="show gateway effective configuration")
def show_gw_effective(group_name):
  resp = gateway.get_config_effective(central,group_name)
  resp = {"cli_cmds": resp["msg"]["config"]}

  pprint(resp)
    
@app.command(help="push configuration from file to AOS10_GW")
def push_config(

    group_name: str = typer.Argument(
        ...,
        help="group/device name of group/device. Ex: Seattle or Seattle/c2:46:65:dc:f8:16"),
    config_file: str = typer.Argument(..., help="json config file to push")
    
):
  resp = caas_push_configuration(group_name,config_file,central.getToken(),central_data1,account_name)


