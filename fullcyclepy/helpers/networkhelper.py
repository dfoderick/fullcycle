'''network related functions, mostly for discovery'''
import socket
import nmap

def localip(dns):
    '''todo: why needs dns to find out local ip?'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((dns, 80))
    locip = sock.getsockname()[0]
    sock.close()
    return locip

def networkmap(dns, api_port, ssh_port):
    '''see if scanning for ssh port is really necessary'''
    locip = localip(dns)
    print('Your ip is {0}'.format(locip))
    #scan can take a minute
    #-n/-R: Never do DNS resolution/Always resolve [default: sometimes]
    #-sL: List Scan - simply list targets to scan
    #-sP <hosts>: only does discovery
    #-PS: Port scan during discovery
    scanarguments = '-v -sV' #faster but lists hosts that are not miners
    print("mapping network with arguments '{0}'".format(scanarguments))
    netmapper = nmap.PortScanner()
    netmapper.scan(hosts=locip+'/24', ports='{0},{1}'.format(api_port, ssh_port), arguments=scanarguments, sudo=False)
    hosts_list = [(h, netmapper[h]['status']['state'], netmapper[h]['vendor']) for h in netmapper.all_hosts()]
    return hosts_list
