import re
import json
import sys
from string import Template
import ipaddress

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
        """ Returns an interface name if it is an interface
            Match the following: GigabitEthernet, Loopback,
            Fastethernet, Tengigabitethernet, Vlan, Port-channel  """
        if_name = self.srch_str(pattern=r"^interface [PpTtLlVvFfGg].*", string=line)
        if if_name:
            if_name = if_name[0].split()[1]
            return if_name

    def is_end_of_sub_cfg(self, line):
        """ Checks if sub-configuration is ending, i.e. there's an ! present """
        end_sym = self.srch_str(pattern=r"^!", string=line)
        return end_sym

    def is_hostname(self, line):
        """ Gets the hostname provided """
        hostname = self.srch_str(pattern=r"^hostname.*", string=line)
        if hostname:
            return hostname[0].split('hostname')[1].strip()

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

    def is_access_vlan(self, line):
        """ Returns access vlan number if available  """
        access_vlan = self.srch_str(pattern=r"^ switchport access vlan .*", string=line)
        if access_vlan:
            return access_vlan[0].strip().split('vlan')[1].strip()

    def is_voice_vlan(self, line):
        """ Returns voice vlan number if available"""
        voice_vlan = self.srch_str(pattern=r"^ switchport voice vlan .*", string=line)
        if voice_vlan:
            return voice_vlan[0].strip().split('vlan')[1].strip()

    def is_port_mode(self, line):
        """ Returns port mode: access or trunk """
        port_mode = self.srch_str(pattern=r"^ switchport mode.*", string=line)
        if port_mode:
            return port_mode[0].strip().split('mode')[1].strip()

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
            return 'shutdown'

    def is_snmp_notification_option_add(self, line):
        """ Returns a line if there is an snmp option add  """
        snmp_option_add = self.srch_str(pattern=r"^ snmp trap mac-notification change added", string=line)
        if snmp_option_add:
            return snmp_option_add[0].strip()

    def is_snmp_notification_option_remove(self, line):
        """ Returns a line if there is an snmp option remove  """
        snmp_option_remove = self.srch_str(pattern=r"^ snmp trap mac-notification change remove", string=line)
        if snmp_option_remove:
            return snmp_option_remove[0].strip()

    def is_stree_mode(self, line):
        """ Returns spanning-tree mode """
        stree_mode = self.srch_str(pattern=r"^ spanning-tree.*", string=line)
        if stree_mode:
            return stree_mode[0].strip().split('mode')[1].strip()

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

    def get_hostname(self):
        """ Returns a string object representing the device hostname """
        for line in self.data:
            hostname = self.is_hostname(line)
            if hostname:
                return hostname

    def get_all_interface_properties(self):
        """ Converts the following interface properties to a
            list of dictionaries if property is available :

            - Interface Name
            - Interface Description
            - Interface IP Address and Subnet Mask
            - Interface Speed
            - Interface Duplex
            - Interface VRF Membership
            - Interface State
            - PIM Mode (Multicast)
            - Switchport Mode
            - Switchport Voice and Access Vlans

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
            all_current_int_props = {'name': None}
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
                elif self.is_port_mode(prop):
                    all_current_int_props['mode'] = self.is_port_mode(prop)
                elif self.is_access_vlan(prop):
                    all_current_int_props['access_vlan'] = self.is_access_vlan(prop)
                elif self.is_stree_mode(prop):
                    all_current_int_props['spanning-tree_mode'] = self.is_stree_mode(prop)
                elif self.is_snmp_notification_option_add(prop):
                    all_current_int_props['snmp_opt_add'] = self.is_snmp_notification_option_add(prop)
                elif self.is_snmp_notification_option_remove(prop):
                    all_current_int_props['snmp_opt_remove'] = self.is_snmp_notification_option_remove(prop)
                elif self.is_voice_vlan(prop):
                    all_current_int_props['voice_vlan'] = self.is_voice_vlan(prop)
                elif self.is_vrf_forwarding(prop):
                    all_current_int_props['vrf'] = self.is_vrf_forwarding(prop)
                elif self.is_state(prop):
                    all_current_int_props['state'] = self.is_state(prop)
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


class IOSGenerate(object):
    def __init__(self):
        #self.data = data
        pass

    @staticmethod
    def format_interface_for_write(interface):
        """ Formats a single interface with supported properties when supplied in dictionary format """
        int_cfg_lines = []
        # return key only if exists; else return false
        name = interface.get('name')
        desc = interface.get('description')
        mode = interface.get('mode')
        state = interface.get('state')
        ip = interface.get('ipv4')
        # check if keys exist in interface dictionary; if true, append to
        # list of commands to write
        #
        # properties associated with all interfaces
        if name:
            int_cfg_lines.append('interface {}\n'.format(name))
        if desc:
            int_cfg_lines.append(' description {}\n'.format(desc))
        if state:
            int_cfg_lines.append(' {}\n'.format(state))
        # properties associated with layer two interfaces
        if mode == 'access':
            access_vlan = interface.get('access_vlan')
            voice_vlan = interface.get('voice_vlan')
            snmp_opt_add = interface.get('snmp_opt_add')
            snmp_opt_remove = interface.get('snmp_opt_remove')
            stree_mode = interface.get('spanning-tree_mode')
            int_cfg_lines.append(' switchport access vlan {}\n'.format(access_vlan))
            if mode:
                int_cfg_lines.append(' switchport mode {}\n'.format(mode))
            if voice_vlan:
                int_cfg_lines.append(' switchport voice vlan {}\n'.format(voice_vlan))
            if snmp_opt_add:
                int_cfg_lines.append(' {}\n'.format(snmp_opt_add))
            if snmp_opt_remove:
                int_cfg_lines.append(' {}\n'.format(snmp_opt_remove))
            if stree_mode:
                int_cfg_lines.append(' spanning-tree {}\n'.format(stree_mode))
        # properties associated with layer 3 interfaces
        if ip:
            vrf = interface.get('vrf')
            ip_helpers = interface.get('ip_helpers')
            int_cfg_lines.append(' ip address {} {}\n'.format(ip['ip'], ip['mask']))
            pim_mode = interface.get('pim_mode')
            if vrf:
                int_cfg_lines.append(' vrf forwarding {}\n'.format(vrf))
            if pim_mode:
                int_cfg_lines.append(' ip pim {}\n'.format(pim_mode))
            if ip_helpers:
                for helper in ip_helpers:
                    int_cfg_lines.append(' ip helper-address {}\n'.format(helper))
        int_cfg_lines.append('!')
        int_cfg_lines.append('\n')
        return int_cfg_lines

    @staticmethod
    def format_vnet_for_write(vnet):
        """ Formats a single interface with supported properties when supplied in dictionary format """
        vnet_cfg_lines = []
        name = vnet.get('name')
        ip = vnet.get('ipv4')
        pim_mode = vnet.get('pim_mode')
        if name:
            vnet_cfg_lines.append('vnet name {}\n'.format(name))
        if ip:
            vnet_cfg_lines.append(' ip address {} {}\n'.format(ip['ip'], ip['mask']))
        if pim_mode:
            vnet_cfg_lines.append(' ip pim {}\n'.format(pim_mode))
        vnet_cfg_lines.append('!\n')
        return vnet_cfg_lines

    @staticmethod
    def create_standard_loopback(name, desc, vrf, ipv4, pim_mode, interfaces):
        standard_loopback_interface = {
            'name': name,
            'description': desc,
            'vrf': vrf,
            'ipv4': ipv4,
            'pim_mode': pim_mode
        }
        interfaces.append(standard_loopback_interface)

    @staticmethod
    def create_standard_vnet(name, ipv4, pim_mode):
        vnet_properties = []
        standard_vnet_interface = {
            'name': name,
            'ipv4': ipv4,
            'pim_mode': pim_mode
        }
        vnet_properties.append(standard_vnet_interface)
        return vnet_properties

    def write_cfg(self, cfg_file, lines, type):
        format_line = getattr(IOSGenerate, 'format_{}_for_write'.format(type))
        with open(cfg_file, 'a+') as f:
            for line in lines:
                int_cfg = format_line(line)
                for line in int_cfg:
                    f.write(line)








    



