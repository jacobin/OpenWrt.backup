###############################################################################
import dns.resolver # pip install dnspython
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
# Example usage:
domain = sys.argv[1]
server = '8.8.8.8'

print(f"Querying {domain} using DNS server {server}...")
results = dns_lookup_with_specific_server(domain, server)

print(f"IP addresses for {domain}:")
for ip in results:
    print(f"- {ip}")

################################## END ########################################
