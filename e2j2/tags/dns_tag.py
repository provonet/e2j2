from dns.resolver import Resolver, NoAnswer, NXDOMAIN, Timeout
from e2j2.helpers.exception import E2j2Exception


def parse(config, value):
    resolver = Resolver()
    resolver.nameservers = config['nameservers'] if 'nameservers' in config else resolver.nameservers
    resolver.port = config['port'] if 'port' in config else resolver.port
    rdtype = config['rdtype'] if 'rdtype' in config else 'A'

    try:
        return_values = []
        replies = resolver.query(value, rdtype=rdtype)
        for reply in replies:
            return_value = {}

            if rdtype in ['A', 'AAAA']:
                return_value = {'address': reply.address}
            elif rdtype == 'SRV':
                return_value = {'target': str(reply.target), 'port': reply.port, 'weight': reply.weight,
                                'priority': reply.priority}

            return_values.append(return_value)

    except (NXDOMAIN, NoAnswer, Timeout) as err:
        raise E2j2Exception(str(err))
    except Exception as err:
        raise E2j2Exception('dns_tag failed with: %s' % str(err))

    return return_values
