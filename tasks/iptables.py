import iptc
chain_name = 'FORWARD'

def track_ip(ip):
    chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), chain_name)

    # make sure we don't insert any dupes
    for rule in chain.rules:
        if rule.dst == ip+'/255.255.255.255'\
            or rule.src == ip+'/255.255.255.255':
            # throw an exception
            return "Already tracking this IP (or another rules exists)."
    
    # setup RX
    rule = iptc.Rule()
    rule.create_target("ACCEPT")
    rule.dst = ip
    chain.append_rule(rule)

    # setup TX
    rule = iptc.Rule()
    rule.create_target("ACCEPT")
    rule.src = ip
    chain.append_rule(rule)

    return "Success"

def check_ip(ip):
    chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), chain_name)
    rx = None
    tx = None
    for rule in chain.rules:
        if rule.dst == ip+'/255.255.255.255':
            rx = rule.get_counters()
        elif rule.src == ip+'/255.255.255.255':
            tx = rule.get_counters()
    return (rx, tx) 

def check_all(ip):
    chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), chain_name)
    rx = (0,0)
    tx = (0,0)
    for rule in chain.rules:
        counter = rule.get_counters()
        if rule.dst == '0.0.0.0/0':
            rx[0] += counter[0]
            rx[1] += counter[1]
        else:
            tx[0] += counter[0]
            tx[1] += counter[1]
    return (rx, tx)

def remove_ip(ip):
    chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), chain_name)
    rules = 0
    for rule in chain.rules:
        if rule.dst == ip+'/255.255.255.255':
            chain.delete_rule(rule)
            rules += 1
        elif rule.src == ip+'/255.255.255.255':
            chain.delete_rule(rule)
            rules += 1
    return {'removed': rules}

if __name__ == '__main__':
    track_ip('78.46.207.52')
    track_ip('78.46.207.53')
    track_ip('78.46.207.54')
