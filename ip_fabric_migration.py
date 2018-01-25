from ios_parse import *










if __name__ == '__main__':
    cfg = 'delta_cfg.txt'
    device = NetworkDevice(cfg)
    data = device.load_data()
    ios = IOSParse(data)
    # print(json.dumps(interface_properties, indent=4))
    interface_properties = ios.get_all_interface_properties()
    vnet_properties = []
    hostname = ios.get_hostname()
    config_write = IOSGenerate()


    # changing access vlan from 966 to 777
    for i in interface_properties:
        new_vlan = i.get('access_vlan')
        if new_vlan == '966':
            i['access_vlan'] = 777
            i['ip_helpers'] = ['10.1.1.1', '10.2.2.2']

    print(json.dumps(interface_properties, indent=4))


    # remove standard interface loopbacks and add standard config
    # [:] is for changing the list in place. Otherwise, the indexes will never update and you
    # will get some strange results
    # This list comprehension can also be done with for loop
    standard_loopback_interface_names = ['Loopback0', 'Loopback2', 'Loopback8', 'Loopback10', 'Loopback12']
    interface_properties[:] = [interface for interface in interface_properties
                               if interface.get('name') not in standard_loopback_interface_names]


    #for interface in interface_properties:
    #    print(interface)

    print('---------------------------------')

    new_cfg = 'test.txt'

    # add new loopback interfaces
    config_write.create_standard_loopback(
        name='Loopback100',
        desc='== GLOBAL VRF MGMT INTERFACE ==',
        vrf='mgmt-vrf',
        ipv4={'ip': '1.1.1.1', 'mask': '255.255.255.255'},
        pim_mode='sparse-mode',
        interfaces=interface_properties
    )

    config_write.create_standard_vnet(
        name='USER-VRF',
        ipv4={'ip': '1.1.1.1', 'mask': '255.255.255.255'},
        pim_mode='sparse-mode',
        vnets=vnet_properties
    )
    # # write hostname to configuration file
    # with open(new_cfg, 'w+') as f:
    #     f.write('hostname {}\n!\n'.format(hostname))
    #
    # # write changed interface configuration to configuration file
    # with open(new_cfg, 'a+') as f:
    #     for interface in interface_properties:
    #         int_cfg = config_write.format_interface_for_write(interface)
    #         for line in int_cfg:
    #             f.write(line)
    #
    # # write changed interface configuration to configuration file
    # with open(new_cfg, 'a+') as f:
    #     for vnet in vnet_properties:
    #         vnet_cfg = config_write.format_vnet_for_write(vnet)
    #         for line in vnet_cfg:
    #             f.write(line)



    config_write.write_cfg(new_cfg, interface_properties, 'interface')
    config_write.write_cfg(new_cfg, vnet_properties, 'vnet')



#print(json.dumps(ios.get_interface_properties('loopback30'), indent=4))
#print(json.dumps(ios.get_all_interface_properties(), indent=4))