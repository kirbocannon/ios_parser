import csv
import sys
import ipaddress

csv_filename = 'vlan_info.csv'

def import_csv_by_key(filename, key, value):
    """ Read and return filtered values from  CSV using key/value.
        For example, a key could be 'hostname', while a value could
        be 'my-hostname-1. Only returns back entire items of those results
        which match. """
    try:
        with open(filename, mode='rt') as csv_file:
            reader = csv.DictReader(csv_file, dialect='excel')
            items = [item for item in reader if item[key] == value]
            return items
    except csv.Error as e:
        sys.exit("file {}, line {}: {}".format(filename, reader.line_num, e))
    except FileNotFoundError:
        sys.exit("file '{}' could not be found.".format(filename))

def construct_vlan_ip(vlan_num, vlan_info):
    vlan_obj = {}
    try:
        vlan = next(vlan for vlan in vlan_info if vlan['NEW VLAN ID'] == 'Vlan{}'.format(vlan_num))
        vlan_obj['num'] = vlan_num
        vlan_obj['name'] = vlan['VLAN NAME']
        vlan_obj['ip'] = str(list(ipaddress.ip_network(vlan['SUBNET']).hosts())[0])
        vlan_obj['mask'] = ipaddress.IPv4Interface(vlan['SUBNET']).with_netmask.split('/')[1]
        return vlan_obj
    except StopIteration:
        sys.exit('vlan{} not found'.format(vlan_num))


# print(construct_vlan_ip('51'))
# print(construct_vlan_ip('52'))
# print(construct_vlan_ip('351'))
# print(construct_vlan_ip('55'))





