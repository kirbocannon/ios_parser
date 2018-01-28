import csv
import sys

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



vlan_info = import_csv_by_key(filename=csv_filename, key='NEW SW NAME', value='NYCL-10W-CORP-LF1')

vlan70 = next(vlan for vlan in vlan_info if vlan['VLAN ID'] == 'Vlan70')

print(vlan70['SUBNET'])