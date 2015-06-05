#!/usr/bin/env python3
import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
import argparse
import json
import platform
import os
import requests
import subprocess
DBusGMainLoop(set_as_default=True)
import NetworkManager


NETWORK_CONFIG_DIR = '/etc/netlogin/networks.d'
NETWORK_CONFIG_FILE = '/etc/netlogin/networks.json'
MAIN_CONFIG_FILE = '/etc/netlogin/config.json'

verbosity = 0
networks = {}


system_bus = dbus.SystemBus()


def vprint(*args, at_verbosity=1):
    if verbosity >= at_verbosity:
        print(*args)


def load_config(config_file):
    if os.path.isdir(config_file):
        ret = {}
        for f in os.listdir(config_file):
            fpath = os.path.join(config_file, f)
            with open(fpath) as h:
                ret.update(json.loads(h.read()))
        return ret
    else:
        with open(config_file) as h:
            return json.loads(h.read())


def get_bssid():
    return subprocess.check_output('iwgetid --ap -r').lower()


def get_mac(interface):
    # TODO: implement client mac address finding for non-linux OSes
    if platform.system() == 'Linux':
        with open(os.path.join('/sys/class/net',
                               interface, 'address'), 'r') as h:
            addr = h.read()
            h.close()
            return addr
    else:
        raise NotImplementedError('Unfortunately, other platforms than '
                                  'linux are not yet supported while getting '
                                  'client MAC addresses. Please make a PR if '
                                  'you want to fix this.')


def replace_string(string, replace_str, replace_func):
    if replace_str in string:
        return string.replace(replace_str, replace_func())
    else:
        return string


def replace_url_params(url):
    newurl = url
    replacefuncs = {
        '$ap_mac': get_bssid,
        '$mac': get_mac
    }
    # need to replace ap mac, client mac
    for replacestring, func in replacefuncs.items():
        newurl = replace_string(newurl, replacestring, func)
    return newurl


def check_internet_access(url='http://gstatic.com/generate_204',
                          expect_response_code=204):
    resp = requests.get(url)
    return resp.status_code == expect_response_code


def login_network(**args):
    '''
    Log into a network.

    Parameters:
    url -- URL to send a request to
    method -- method to use
    headers -- headers for the request
    params -- URL parameters
    data -- POST data
    '''
    if check_internet_access():
        # we have internet access, must be logged in
        vprint('Already have internet access...')
        return True
    requests.packages.urllib3.disable_warnings()
    req = requests.Request(**args)
    r = req.prepare()
    s = requests.Session()
    resp = s.send(r, verify=False)
    if resp.status_code >= 200 and resp.status_code < 300:
        vprint('Login succeeded by status code')
        return True
    else:
        vprint('Login failed by status code')
        return False


def handle_nm_propchanged(obj, **kwargs):
    rejections = [
        # Filter most stuff we don't care about
        'ActiveConnections' not in obj,
        # Ignore connection activation, we need an actual connection
        'ActivatingConnection' in obj,
        # No active connections
        'ActiveConnections' in obj and obj['ActiveConnections'] == [],
        # Wireless is disabled
        'WirelessEnabled' in obj and obj['WirelessEnabled'] is False,
    ]

    for key, rej in enumerate(rejections):
        if rej:
            vprint('Rejecting message: reason', key, at_verbosity=4)
            return

    vprint('Got an accepted PropertiesChanged. Handling network.',
           at_verbosity=4)
    for c in obj['ActiveConnections']:
        if c.Type != '802-11-wireless':
            continue
        if c.SpecificObject.__class__.__name__ == 'AccessPoint':
            login_ssid = c.SpecificObject.Ssid
            if login_ssid not in networks:
                print('No config for ', login_ssid, ', skipping...', sep='')
                continue
            print('Logging into network', login_ssid)
            login_network(**networks[login_ssid])


def get_connected_ssids():
    active_connections = NetworkManager.NetworkManager.ActiveConnections
    ssids = []
    for conn in active_connections:
        if conn.SpecificObject.__class__.__name__ == 'AccessPoint':
            ssids.append(conn.SpecificObject.Ssid)
    return ssids


def register_signal_handler():
    d_args = ('sender', 'destination', 'interface', 'member', 'path')
    d_args = dict([(x + '_keyword', 'd_' + x) for x in d_args])
    NetworkManager.NetworkManager.connect_to_signal('PropertiesChanged',
                                                    handle_nm_propchanged,
                                                    **d_args)


def main():
    global verbosity
    parse = argparse.ArgumentParser(description='Log into WiFi networks '
                                                'automatically')
    parse.add_argument('--listen', '--daemon', '-l',
                       help='Set up an event listener on NetworkManager and '
                       'automatically login when connecting',
                       action='store_true')
    parse.add_argument('--network', '-n', help='Log into network '
                                               'provided, without setting '
                                               'an event listener')
    parse.add_argument('--verbose', '-v', help='Verbosity level',
                       action='count')
    args = parse.parse_args()
    verbosity = args.verbose if args.verbose else 0
    # Load network configs
    if os.path.exists(NETWORK_CONFIG_DIR):
        networks.update(load_config(NETWORK_CONFIG_DIR))
    if os.path.exists(NETWORK_CONFIG_FILE):
        networks.update(load_config(NETWORK_CONFIG_FILE))

    if args.listen and not args.network:
        register_signal_handler()
        loop = GObject.MainLoop()
        loop.run()
    elif not (args.listen or args.network):
        connected_ssids = get_connected_ssids()
        for ssid in connected_ssids:
            if ssid not in networks:
                print('No configuration for network ', ssid, ', skipping',
                      sep='')
                # having an unconfigured ssid will be a problem later
                connected_ssids.remove(ssid)
                continue
            networks[ssid] = {
                k: replace_url_params(x) for k, x in networks[ssid].items()}
        [login_network(**networks[x]) for x in connected_ssids]
    else:
        if args.network not in networks:
            raise KeyError('No configuration for network: ' + args.network)
        networks[args.network] = {
            x: replace_url_params(y) for x, y in networks[args.network].items()
        }
        if login_network(**networks[args.network]):
            print('Logged into network', args.network, 'successfully')
        else:
            print('Failure when logging into network', args.network)


if __name__ == '__main__':
    main()
