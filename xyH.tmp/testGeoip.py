###############################################################################
import dns.resolver # pip install dnspython
import geoip2.database
import geoip2.errors
import socket
import sys


###############################################################################
def dns_lookup_with_specific_server(domain_name, dns_server_ip):
    '''
    Performs a DNS A record lookup for a domain using a specified DNS server.
    '''
    # Create a custom resolver object
    my_resolver = dns.resolver.Resolver()

    # Force the resolver to use the specified IP address
    my_resolver.nameservers = [dns_server_ip]

    try:
        # Perform the query for an A record (IPv4 address)
        answers = my_resolver.resolve(domain_name, 'A')

        ip_addresses = [str(answer) for answer in answers]
        return ip_addresses

    except dns.resolver.LifetimeTimeout:
        return [f"Error: DNS server {dns_server_ip} timed out"]
    except Exception as e:
        return [f"Error during DNS resolution: {e}"]


###############################################################################
hostname = sys.argv[1]

try:
    ip = dns_lookup_with_specific_server(hostname, "8.8.8.8")
    print(f"The IP address of \"{hostname}\" is {ip}")
except socket.gaierror as e:
    print(f"Error resolving the hostname \"{hostname}\": {e}")
    sys.exit(1)

geo_db_path = 'GeoLite2-City.mmdb'

try:
    with geoip2.database.Reader(geo_db_path) as reader:
        response = reader.city(ip[0])
        print("Retrieve infomation from geo:")
        print(f"\tIP Address: {ip[0]}")
        print(f"\tCountry Name: {response.country.name}")
        print(f"\tCity Name: {response.city.name}")
        print(f"\tLatitude: {response.location.latitude}")
        print(f"\tLongitude: {response.location.longitude}")
except geoip2.errors.AddressNotFoundError:
    print(f"Location for IP {ip[0]} not found in the database.")
except Exception as e:
    print(f"An error occurred: {e}")
