from dns.resolver import Resolver, NoAnswer, NXDOMAIN, Timeout
from e2j2.exceptions import E2j2Exception


def parse(tag_config, value):
    resolver = Resolver()
    resolver.nameservers = tag_config['nameservers'] if 'nameservers' in tag_config else resolver.nameservers
    resolver.port = tag_config['port'] if 'port' in tag_config else resolver.port
    rdtype = tag_config['type'] if 'type' in tag_config else 'A'

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

    except (NXDOMAIN, NoAnswer) as err:
        raise E2j2Exception(str(err))
    except Timeout as err:
        # strip number of seconds
        raise E2j2Exception('The DNS operation timed out')
    except Exception as err:
        raise E2j2Exception('dns_tag failed with: %s' % str(err))

    return return_values
