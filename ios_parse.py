import re
import json


cfg = 'delta_cfg.txt'



class NetworkDevice(object):
    def __init__(self, config):
        self.config = config

    def load_data(self):
        with open(self.config, 'r') as f:
            data = f.readlines()
        return data


class IOSParse(object):
    def __init__(self, data):
        self.data = data

    def srch_str(self, pattern, string):
        match = re.findall(pattern, string)
        return match

    def is_int(self, line):
        """ Returns an interface name if it is an interface """
        if_name = self.srch_str(pattern=r"^interface .*", string=line)
        if if_name:
            if_name = if_name[0].split()[1]
            return if_name

#    def is_protocol(self, line):
#        """ Returns a line if it is a routing protocol  """
#        return self.srch_str(pattern=r"^router", string=line)

    def is_int_ip(self, line):
        """ Returns a line if it is an interface IP address
            Important to note that this will fail on 111.111.111.345 (outside IP address) """
        """ Maybe need to fix for secondary ip addresses """
        ip_address = {'ip': '', 'mask': ''}
        int_ip = self.srch_str(pattern=r"^ ip address \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} "
                                    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", string=line)
        if int_ip:
            int_ip_address = int_ip[0].strip().split()[2]
            int_subnet_mask = int_ip[0].strip().split()[3]
            ip_address['ip'] = int_ip_address
            ip_address['mask'] = int_subnet_mask
            return ip_address
        else:
            return "No IP Address"

    def is_duplex(self, line):
        """ Returns a line if it is a duplex setting """
        duplex = self.srch_str(pattern=r"^ duplex.*", string=line)
        if duplex:
            duplex = duplex[0].strip().split()[1]
            return duplex

    def is_speed(self, line):
        """ Returns a line if it is a speed setting """
        speed = self.srch_str(pattern=r"^ speed.*", string=line)
        if speed:
            speed = speed[0].strip().split()[1]
            return speed

    def create_obj_list(self, obj_type):
        """ Creates an object list out of objects such as interfaces """
        data = self.data
        if obj_type == 'INTERFACES':
            return [obj.strip().split()[1] for obj in data if self.is_int(obj)]
        #elif obj_type == 'PROTOCOLS':
        #    return [obj.strip().split()[1] for obj in data if self.is_protocol(obj)]

    def get_interfaces(self):
        """ Gets a list of all interfaces without interface properties """
        interfaces = self.create_obj_list('INTERFACES')
        return interfaces

#    def get_protocols(self):
#        """ Gets a list of all routing protocols without protocol properties  """
#        protocols = self.create_obj_list('PROTOCOLS')
#        return protocols

    def get_interface_ips(self):
        """ Gets a list of all ips configured on the device """
        pass

    #def get_interface_ip(self, interface):
    #    interface_ip = self.is_int_ip('INTERFACE')
    #    return interface_ip

    def get_all_interface_properties(self):
        """ Converts the following interface properties to a
            list of  Dictionaries:

            - Interface Name
            - Interface IP Address and Subnet Mask
            - Interface speed
            - Interface duplex

        """
        data = self.data
        idx = 0
        if_props_list = []
        for line in data:
            # check if IP address is present
            if self.is_int(line):
                if_name = self.is_int(data[idx])
                if_ip = self.is_int_ip(data[idx + 1])
                if if_ip:
                    if_props = {}
                    if_ip = if_ip
                    if_props['if_name'] = if_name
                    if_props['ip4'] = if_ip
                    if_props_list.append(if_props)
                else:
                    if_props = {}
                    if_name = if_name
                    if_props['if_name'] = if_name
                    if_props_list.append(if_props)
                # check duplex settings
                if_duplex = self.is_duplex(data[idx + 2])
                if if_duplex:
                    if_props['duplex'] = if_duplex
                # check speed settings
                if_speed = self.is_speed(data[idx + 3])
                if if_duplex:
                    if_props['speed'] = if_speed
            idx +=1
        return if_props_list

    def get_interface_properties(self, interface_name):
        all_interfaces = self.get_all_interface_properties()
        try:
            interface = next(interface for interface in all_interfaces
                             if interface['if_name'].lower() == interface_name.lower())
            return interface
        except StopIteration:
            print('Interface {} Not Found.'.format(interface_name))






def convert_to_dict(objects):
    obj_dict = {}
    cnt = 1
    for obj in objects:
        obj_dict[cnt] = obj
        cnt+=1
    return json.dumps(obj_dict, indent=4)


device = NetworkDevice(cfg)
data = device.load_data()
ios = IOSParse(data)
interfaces = ios.get_interfaces()


test = convert_to_dict(interfaces)

#interface_properties = ios.get_all_interface_properties()
#print(json.dumps(interface_properties, indent=4))

print(json.dumps(ios.get_interface_properties('loopback30')))


print(json.dumps(ios.get_all_interface_properties(), indent=4))



#for interface in interfaces:
#    print(interface)


    



