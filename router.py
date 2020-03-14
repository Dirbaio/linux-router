import json
import os
import errno
import subprocess

from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader('templates'),
    line_statement_prefix="!",
)

root = '/'

def render_template(src, dst, **kwargs):
    dst = root + dst
    try:
        os.remove(dst)  # Remove it in case it's a symlink
    except OSError:
        pass  # If it doesn't exist, no worries.

    try:
        os.makedirs(os.path.dirname(dst))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    kwargs['config'] = config

    with open(dst, 'wt') as f:
        res = env.get_template(src).render(**kwargs)
        indent = 0
        for l in res.split('\n'):
            nopen = l.count('{') + l.count('(')
            nclose = l.count('}') + l.count(')')

            if nopen == 0:
                indent -= nclose

            f.write('    '*indent)
            f.write(l.strip())
            f.write('\n')

            if nopen != 0:
                indent += nopen-nclose

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Check interface uses
    ifaces = {}
    for iface in config['interfaces']:
        t = iface['type']
        n = iface['name']
        if t == 'hardware':
            ifaces[iface['name']] = ''
        elif t == 'vlan':
            assert ifaces[iface['parent']] in ('', 'vlan')
            ifaces[iface['parent']] = 'vlan'
            ifaces[iface['name']] = ''
        elif t == 'pppoe':
            assert ifaces[iface['parent']] == ''
            ifaces[iface['parent']] = 'pppoe'
            ifaces[iface['name']] = ''
        else:
            assert False

    for network in config['networks']:
        assert ifaces[network['interface']] == ''
        ifaces[network['interface']] = 'network'

    # VLAN stuff
    for name, use in ifaces.items():
        if use == 'vlan':
            render_template('networkd/vlan.network', '/etc/systemd/network/{}.network'.format(name), interface={'name': name})
    for interface in config['interfaces']:
        if interface['type'] == 'vlan':
            render_template('networkd/vlan.netdev', '/etc/systemd/network/{}.netdev'.format(interface['name']), interface=interface)

    # PPP stuff
    render_template('ppp/ppp@.service', '/etc/systemd/system/ppp@.service')
    render_template('ppp/secrets', '/etc/ppp/pap-secrets')
    render_template('ppp/secrets', '/etc/ppp/chap-secrets')
    for interface in config['interfaces']:
        if interface['type'] == 'pppoe':
            render_template('ppp/peer', '/etc/ppp/peers/'+interface['name'], interface=interface)

    # NETWORKS
    for network in config['networks']:
        render_template('networkd/network', '/etc/systemd/network/{}.network'.format(network['interface']), network=network)

    render_template('udev.rules', '/etc/udev/rules.d/10-router.rules')
    render_template('resolv.conf', '/etc/resolv.conf')
    render_template('hosts', '/etc/hosts')
    render_template('dnsmasq.conf', '/etc/dnsmasq.conf')
    render_template('nftables.conf', '/etc/nftables.conf')

    subprocess.call('systemctl restart nftables', shell=True)
    subprocess.call('systemctl restart dnsmasq', shell=True)
