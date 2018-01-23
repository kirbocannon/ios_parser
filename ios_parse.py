import re
import json
from copy import deepcopy


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

    def is_end_of_sub_cfg(self, line):
        """ Checks if sub-configuration is ending, i.e. there's an ! present """
        end_sym = self.srch_str(pattern=r"^!", string=line)
        return end_sym

#    def is_protocol(self, line):
#        """ Returns a line if it is a routing protocol  """
#        return self.srch_str(pattern=r"^router", string=line)

    def is_int_ip(self, line):
        """ Returns a line if it is an interface IP address
            Important to note that this will fail on 111.111.111.345 (outside IP address) """
        """ Maybe need to fix for secondary ip addresses """
        ip_addr = {'ip': '', 'mask': ''}
        int_ip = self.srch_str(pattern=r"^ ip address \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} "
                                    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", string=line)
        if int_ip:
            int_ip_addr = int_ip[0].strip().split()[2]
            int_subnet_mask = int_ip[0].strip().split()[3]
            ip_addr['ip'] = int_ip_addr
            ip_addr['mask'] = int_subnet_mask
            return ip_addr

    def is_duplex(self, line):
        """ Returns a line if it is a duplex setting """
        duplex = self.srch_str(pattern=r"^ duplex.*", string=line)
        if duplex:
            return duplex[0].strip().split()[1]

    def is_speed(self, line):
        """ Returns a line if it is a speed setting """
        speed = self.srch_str(pattern=r"^.speed.*", string=line)
        if speed:
            return speed[0].strip().split()[1]

    def is_description(self, line):
        """ Returns a line if it is a description """
        desc = self.srch_str(pattern=r"^ description.*", string=line)
        if desc:
            return desc[0].strip().split('description')[1].strip()

    def is_state(self, line):
        """ Returns a line if interface is shutdown  """
        state = self.srch_str(pattern=r"^ shutdown.*", string=line)
        if state:
            return True

    def is_pim_mode(self, line):
        """ Returns a line if interface is shutdown  """
        pim_mode = self.srch_str(pattern=r"^ ip pim.*", string=line)
        if pim_mode:
            return pim_mode[0].strip().split('ip pim')[1].strip()

    def is_vrf_forwarding(self, line):
        """ Returns a line if it is a speed setting """
        vrf_fwd = self.srch_str(pattern=r"^ vrf forwarding.*", string=line)
        if vrf_fwd:
            return vrf_fwd[0].strip().split('forwarding')[1].strip()

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
            - Interface Description
            - Interface IP Address and Subnet Mask
            - Interface Speed
            - Interface Duplex
            - Interface VRF Membership
            - Interface State
            - PIM Mode (Multicast)

        """
        data = self.data
        start_idx_loc_lst = []
        end_idx_loc_lst = []
        # get indexes for all interfaces
        for idx, line in enumerate(data):
            if self.is_int(line):
                start_idx_loc_lst.append(idx)
        # get indexes for all '!' in configuration
        for idx, i in enumerate(data):
            if i.strip() == '!':
                end_idx_loc_lst.append(idx)
        # start index for index should never be more than '!' end, so remove these from list
        fst_int_idx = start_idx_loc_lst[0]
        end_idx_loc_lst = [x for x in end_idx_loc_lst if x > fst_int_idx]
        #int_idx_list = end_idx_loc_lst[:len(end_idx_loc_lst)]
        idx = 0
        if_props_processed = []
        # iterate through indexes were interfaces start, make list of interface properties
        # until '!' index is reached, then repeat same process for all other interface start indexes
        for int_idx in start_idx_loc_lst:
            if_props = data[int_idx:end_idx_loc_lst[idx]]
            all_current_int_props = {'name': None, 'ipv4': None}
            # check every child item under the interface for the various properties
            for prop in if_props:
                if self.is_int(prop):
                    all_current_int_props['name'] = self.is_int(prop)
                elif self.is_description(prop):
                    all_current_int_props['description'] = self.is_description(prop)
                elif self.is_int_ip(prop):
                    all_current_int_props['ipv4'] = self.is_int_ip(prop)
                elif self.is_duplex(prop):
                    all_current_int_props['duplex'] = self.is_duplex(prop)
                elif self.is_speed(prop):
                    all_current_int_props['speed'] = self.is_speed(prop)
                elif self.is_vrf_forwarding(prop):
                    all_current_int_props['vrf'] = self.is_vrf_forwarding(prop)
                elif self.is_state(prop):
                    all_current_int_props['shutdown'] = self.is_state(prop)
                elif self.is_pim_mode(prop):
                    all_current_int_props['pim_mode'] = self.is_pim_mode(prop)
            if_props_processed.append(all_current_int_props)
            idx += 1
        return if_props_processed

    def get_interface_properties(self, interface_name):
        """ Gets single interface when user provides valid interface name as argument """
        all_interfaces = self.get_all_interface_properties()

        try:
            interface = next(interface for interface in all_interfaces
                             if interface['name'].lower() == interface_name.lower())
            return interface
        except StopIteration:
            print('Interface {} Not Found.'.format(interface_name))





if __name__ == '__main__':


    device = NetworkDevice(cfg)
    data = device.load_data()
    ios = IOSParse(data)
    interfaces = ios.get_interfaces()


    interface_properties = ios.get_all_interface_properties()
    print(json.dumps(interface_properties, indent=4))

    #print(json.dumps(ios.get_interface_properties('loopback30'), indent=4))






#print(json.dumps(ios.get_all_interface_properties(), indent=4))



    



