from ios_parse import *
from shutil import copyfile
import ipaddress


def calc_bgp_ips(vrf_name, bgp_ip):
    """ Calculates BGP IPs needed for BGP leaf/spin setup
        +10 for third octet for the BGP subnet
        For neighbor IPs, it's +34, +36, +38, +40 """
    neighbor_ips = []
    octets = bgp_ip.split('.')
    # vendor calculation is different from all other vrfs
    if vrf_name == 'VEND':
        third_octet = str(int(octets.pop(2)) + 60)
    else:
        third_octet = str(int(octets.pop(2)) + 10)
    octets.insert(2, third_octet)
    bgp_ip = '.'.join(octets)
    # calculate neighbor IPs
    neighbor_one_ip = ipaddress.ip_address(bgp_ip) + 34
    neighbor_two_ip = ipaddress.ip_address(bgp_ip) + 36
    neighbor_three_ip = ipaddress.ip_address(bgp_ip) + 38
    neighbor_four_ip = ipaddress.ip_address(bgp_ip) + 40
    # convert IPs to strings and added to neighbor list
    neighbor_ips.append(neighbor_one_ip.exploded)
    neighbor_ips.append(neighbor_two_ip.exploded)
    neighbor_ips.append(neighbor_three_ip.exploded)
    neighbor_ips.append(neighbor_four_ip.exploded)
    return neighbor_ips

def write_standard_bgp_config(vrf_name, router_id, cfg_file):
    vars = dict()
    cnt = 1
    neighbor_ips = calc_bgp_ips(vrf_name, router_id)
    vars['{}VrfRouterId'.format(vrf_name.lower())] = router_id
    for neighbor_ip in neighbor_ips:
       vars['{}VrfNeighborIp{}'.format(vrf_name.lower(), cnt)] = neighbor_ip
       cnt +=1
    with open(cfg_file, 'r') as f:
        data = f.read()
    with open(cfg_file, encoding='utf-8', mode='w+') as f:
        f.write(Template(data).safe_substitute(vars))







if __name__ == '__main__':
    cfg = 'delta_cfg.txt'
    device = NetworkDevice(cfg)
    data = device.load_data()
    ios = IOSParse(data)
    # print(json.dumps(interface_properties, indent=4))
    interface_properties = ios.get_all_interface_properties()
    hostname = ios.get_hostname()
    cfg_gen = IOSGenerate()


    # changing access vlan from 966 to 777
    for i in interface_properties:
        new_vlan = i.get('access_vlan')
        if new_vlan == '966':
            i['access_vlan'] = 777
            i['ip_helpers'] = ['10.1.1.1', '10.2.2.2']

    #print(json.dumps(interface_properties, indent=4))


    # remove standard interface loopbacks and add standard config
    # [:] is for changing the list in place. Otherwise, the indexes will never update and you
    # will get some strange results
    # This list comprehension can also be done with for loop
    standard_loopback_interface_names = ['Loopback0', 'Loopback2', 'Loopback8', 'Loopback10', 'Loopback12']
    interface_properties[:] = [interface for interface in interface_properties
                               if interface.get('name') not in standard_loopback_interface_names]
    #print('---------------------------------')

    # specify new config file name, copy from base config
    new_cfg = 'test.txt'
    copyfile('base_cfg.txt', new_cfg)

    # add new loopback interfaces
    cfg_gen.create_standard_loopback(
        name='Loopback2',
        desc='== GLOBAL VRF MGMT INTERFACE ==',
        vrf='mgmt-vrf',
        ipv4={'ip': '1.1.1.1', 'mask': '255.255.255.255'},
        pim_mode='sparse-mode',
        interfaces=interface_properties
    )

    vnet1 = cfg_gen.create_standard_vnet(
        name='USER-VRF',
        ipv4={'ip': '1.1.1.1', 'mask': '255.255.255.255'},
        pim_mode='sparse-mode'
    )
    vnet2 = cfg_gen.create_standard_vnet(
        name='MY',
        ipv4={'ip': '2.2.2.2', 'mask': '255.255.255.0'},
        pim_mode='sparse-mode'
    )

    bgp_global = write_standard_bgp_config(
        vrf_name = 'GLOBAL',
        router_id = '10.100.100.110',
        cfg_file =new_cfg
    )
    bgp_user = write_standard_bgp_config(
        vrf_name = 'USER',
        router_id = '10.100.101.110',
        cfg_file =new_cfg
    )
    bgp_fac = write_standard_bgp_config(
        vrf_name = 'FAC',
        router_id = '10.100.104.110',
        cfg_file = new_cfg
    )
    bgp_sec = write_standard_bgp_config(
        vrf_name = 'SEC',
        router_id = '10.100.105.110',
        cfg_file = new_cfg
    )
    bgp_vend = write_standard_bgp_config(
        vrf_name = 'VEND',
        router_id = '10.55.55.110',
        cfg_file = new_cfg
    )




    cfg_gen.write_cfg(new_cfg, interface_properties, 'interface')
    cfg_gen.write_cfg(new_cfg, vnet1, 'vnet')
    cfg_gen.write_cfg(new_cfg, vnet2, 'vnet')




# ip address calculation for vlans is first IP in subnet
# hostname example:
# - nysw731-10wa-corp --> NYCL-10W-CORP-LF1
# - nysw731-10wb-corp --> NYCL-10W-CORP-LF2

"""
interface vlan53
 description <>
 vrf forwading <>
 ip address <>
 ip helper-address <>
 ip helper-address <>
 ip helper-address <>
 ip helper-address <>
 ip helper-address <>
 no ip redirects
 no ip unreachables
 ip directed-broadcast 101
 no ip proxy-arp
 ip pim dr-priority 130
 ip pim sparse-mode
 no autostate
 no shutdown
 !



"""



#print(json.dumps(ios.get_interface_properties('loopback30'), indent=4))
#print(json.dumps(ios.get_all_interface_properties(), indent=4))