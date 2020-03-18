import requests
import json


internal_ip = ['1.1.1.1','1.1.1.3','1.1.1.4','1.1.1.5','1.1.1.2']
external_ip = ['2.2.2.1','2.2.2.2','2.2.2.3','2.2.2.4']

url='https://10.207.195.204:8443//ins'
switchuser='cisco'
switchpassword='cisco'

myheaders={'content-type':'application/json'}
payload = {
  "ins_api": {
    "version": "1.0",
    "type": "cli_show",
    "chunk": "0",
    "sid": "1",
    "input": "show itd",
    "output_format": "json"
  }
}

input = "config terminal ;itd device-group ITDGROUP ;node ip NODEIP"
delete_input = "config terminal ;itd device-group ITDGROUP ;no node ip NODEIP"


response = requests.post(url = url, data=json.dumps(payload), headers = myheaders, verify = False, auth=(switchuser,switchpassword))
json_data = json.loads(response.text)
row_summary = json_data['ins_api']['outputs']['output']['body']['TABLE_summary']['ROW_summary']
for item in row_summary:
    # Check first ITDServices1
    if (item['service_name'] == 'ITDService1'):
        try:
            ROW_vip_node = item['TABLE_vip']['ROW_vip']['TABLE_vip_node']['ROW_vip_node']
            vip_node_list = []
            #Add IPs to Device-Group that are in internal_ip but not in node ip list
            if isinstance(ROW_vip_node, dict):
                vip_node_list.append(ROW_vip_node['vip_node'].split()[-1])
                nodes_to_add = list(set(internal_ip).difference(vip_node_list))
            if isinstance(ROW_vip_node, list):
                for ip in ROW_vip_node:
                    vip_node_list.append(ip['vip_node'].split()[-1])
                nodes_to_add = list(set(internal_ip).difference(vip_node_list))

            for item in nodes_to_add:
                new_input = input.replace('ITDGROUP','ITDDG1').replace('NODEIP', item)
                payload_add_node = {
                                    "ins_api": {
                                        "version": "1.0",
                                        "type": "cli_conf",
                                        "chunk": "0",
                                        "sid": "1",
                                        "input": new_input,
                                        "output_format": "json"
                                        }
                                    }
                response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))

            #Delete IPs from Device-Group that are in node ip list but not in internal_ip
            nodes_to_delete = list(set(vip_node_list).difference(internal_ip))

            for item in nodes_to_delete:
                new_input = delete_input.replace('ITDGROUP','ITDDG1').replace('NODEIP', item)
                payload_add_node = {
                                    "ins_api": {
                                        "version": "1.0",
                                        "type": "cli_conf",
                                        "chunk": "0",
                                        "sid": "1",
                                        "input": new_input,
                                        "output_format": "json"
                                        }
                                    }
                response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))
        except KeyError:
            #If there are no nodes configured, add internal and external IP's from FTD to device-group accordingly
            print("Error, key was not found")
            for item in internal_ip:
                new_input = input.replace('ITDGROUP','ITDDG1').replace('NODEIP', item)
                payload_add_node = {
                                "ins_api": {
                                    "version": "1.0",
                                    "type": "cli_conf",
                                    "chunk": "0",
                                    "sid": "1",
                                    "input": new_input,
                                    "output_format": "json"
                                    }
                                }
                response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))
                
            for item in external_ip:
                new_input = input.replace('ITDGROUP','ITDDG2').replace('NODEIP', item)
                payload_add_node = {
                    "ins_api": {
                        "version": "1.0",
                        "type": "cli_conf",
                        "chunk": "0",
                        "sid": "1",
                        "input": new_input,
                        "output_format": "json"
                        }
                    }
                response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))


    # Now we check ITDServices2
    else:
        if (item['service_name'] == 'ITDService2'):
            try:
                ROW_vip_node = item['TABLE_vip']['ROW_vip']['TABLE_vip_node']['ROW_vip_node']
                vip_node_list = []
                #Add IPs to Device-Group that are in external_ip but not in node ip list
                if isinstance(ROW_vip_node, dict):
                    vip_node_list.append(ROW_vip_node['vip_node'].split()[-1])
                    nodes_to_add = list(set(external_ip).difference(vip_node_list))
                if isinstance(ROW_vip_node, list):
                    for ip in ROW_vip_node:
                        vip_node_list.append(ip['vip_node'].split()[-1])
                    nodes_to_add = list(set(external_ip).difference(vip_node_list))

                for item in nodes_to_add:
                    new_input = input.replace('ITDGROUP','ITDDG2').replace('NODEIP', item)
                    payload_add_node = {
                                        "ins_api": {
                                            "version": "1.0",
                                            "type": "cli_conf",
                                            "chunk": "0",
                                            "sid": "1",
                                            "input": new_input,
                                            "output_format": "json"
                                            }
                                        }
                    response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))

                #Delete IPs from Device-Group that are in node ip list but not in external_ip
                nodes_to_delete = list(set(vip_node_list).difference(external_ip))

                for item in nodes_to_delete:
                    new_input = delete_input.replace('ITDGROUP','ITDDG2').replace('NODEIP', item)
                    payload_add_node = {
                                        "ins_api": {
                                            "version": "1.0",
                                            "type": "cli_conf",
                                            "chunk": "0",
                                            "sid": "1",
                                            "input": new_input,
                                            "output_format": "json"
                                            }
                                        }
                    response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))
            except KeyError:
                #If there are no nodes configured, add internal and external IP's from FTD to device-group accordingly
                print("Error, key was not found")
                for item in internal_ip:
                    new_input = input.replace('ITDGROUP','ITDDG1').replace('NODEIP', item)
                    payload_add_node = {
                                    "ins_api": {
                                        "version": "1.0",
                                        "type": "cli_conf",
                                        "chunk": "0",
                                        "sid": "1",
                                        "input": new_input,
                                        "output_format": "json"
                                        }
                                    }
                    response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))
                    
                for item in external_ip:
                    new_input = input.replace('ITDGROUP','ITDDG2').replace('NODEIP', item)
                    payload_add_node = {
                        "ins_api": {
                            "version": "1.0",
                            "type": "cli_conf",
                            "chunk": "0",
                            "sid": "1",
                            "input": new_input,
                            "output_format": "json"
                            }
                        }
                    response = requests.post(url = url, data=json.dumps(payload_add_node), headers = myheaders, verify = False, auth=(switchuser,switchpassword))
