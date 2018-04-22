'''do the discovery workflow, but bypassing the queue'''

#do not remove! needed
import json #pylint: disable=unused-import
from helpers.networkhelper import networkmap
from fcmapp import ApplicationService
from doflow_handlemessages import dispatchmessages

from when_discover import findminers

def main():
    mainapp = ApplicationService(component='discover', option='')

    mainapp.cacheclear()

    #this is the discovery process
    hosts_list = networkmap(mainapp.configuration('discover.dns'), \
        mainapp.configuration('discover.minerport'), \
        mainapp.configuration('discover.sshport'))
    discoveredentries = findminers(hosts_list, mainapp.knownminers())
    dispatchmessages(mainapp, discoveredentries)
    print('done')


if __name__ == "__main__":
    main()
