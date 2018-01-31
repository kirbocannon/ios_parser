import re
import json
from string import Template
import ipaddress


def read_config(cfg):
    with open(cfg, 'r') as f:
        cfg_lines = f.readlines()
        cfg_lines = [line.rstrip() for line in cfg_lines]
    return cfg_lines


class IOSParse(object):
    def __init__(self, cfg, supp_types_json):
        self.cfg = read_config(cfg)
        self.supp_types_json = json.load(open(supp_types_json))

    def srch_for_supp_obj_prop(self, category, key, line):
        instructions = self.supp_types_json[category]['properties'][key]['read']
        match = re.findall(instructions, line)
        try:
            return match[0].strip()
        except IndexError:
            pass

    def get_interface_names(self):
        """ Returns a list of all the interface names found in a configuration file """
        interface_list = []
        for line in self.cfg:
            if self.srch_for_supp_obj_prop('ios_interface', 'name', line):
                interface_list.append(line.rstrip())
        return interface_list

    def get_interface_properties(self):
        """ Fetches and returns in a dict all interfaces found in a configuration file and returns a list
            You will not get the results you want if you do not conform to the IOS output. This function
            is best suited for reading directly from backup configuration file.
            An '!' symbols end of interface.

            Example:

            switch#show run
            !
            interface Vlan40
             description DATA VLAN
             ip address 192.168.1.1 255.255.255.0
             no ip redirects
            !
            interface GigabitEthernet0/1
             description CORPORATE TRUNK
             switchport mode trunk
             spanning-tree mode trunk
            !
             """
        interfaces_properties_list = []
        properties = {}
        for line in self.cfg:
            for k, v in self.supp_types_json['ios_interface']['properties'].items():
                match = self.srch_for_supp_obj_prop('ios_interface', k, line)
                if match:
                    # if key is already found, just append to the value, helpful when analyzing
                    # commands that can be entered multiple times, such as the ip helper-address command
                    if properties.get(k):
                        properties[k] += ",{}".format(match)
                    else:
                        properties[k] = match
                elif line == '!' and properties.get('name'):
                    interfaces_properties_list.append(properties)
                    properties = {}
        return interfaces_properties_list













net_device1 = IOSParse('delta_cfg.txt', 'supported_types.json')
#test = net_device1.search_for_supp_obj('ios_interface_instructions', 'name')
all_interfaces = net_device1.get_interface_names()
test = net_device1.get_interface_properties()
print(json.dumps(test, indent=4))
# for i in test:
#     print(json.dumps(i, indent=4))



match = re.findall('^ description (.*)', ' description blah392940249 kljdslf;akjsd f8429048u0044')
print(match)





