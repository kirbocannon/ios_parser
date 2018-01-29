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





