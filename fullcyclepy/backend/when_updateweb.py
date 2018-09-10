'''checks for web update'''
import json
import docker
from helpers.queuehelper import QueueName
from backend.fcmapp import Component

COMPONENTUPDATE = Component('fullcycle')

def when_updateweb(channel, method, properties, body):
    '''event handler when updateweb event is raised'''
    try:
        print("[{0}] Received update web message".format(COMPONENTUPDATE.app.now()))
        doupdateweb(body.decode())
    except Exception as ex:
        COMPONENTUPDATE.app.logexception(ex)

def doupdateweb(msg):
    '''check if web app should be updated'''
    doupdate = False
    repository_name = COMPONENTUPDATE.app.configuration('update.fullcycleweb.name.repository')
    client = docker.client.APIClient()

    webstatus = client.pull(repository_name)
    print(webstatus)
    for line in webstatus.splitlines():
        jline = json.loads(line)
        if 'status' in jline and jline['status'].startswith('Status'):
            print(jline['status'])
            doupdate = jline['status'].find('is up to date') < 0

    if doupdate:
        COMPONENTUPDATE.app.alert('Web application needs update')
        container_name = COMPONENTUPDATE.app.configuration('update.fullcycleweb.name.container')
        try:
            #docker stop
            client.stop(container_name)
            #docker rm
            client.remove_container(container_name)
        except BaseException:
            pass
        #docker pull
        client.pull(repository_name)
        #docker run --name fullcycleweb -d --network=host --restart unless-stopped fullcycle/web
        client = docker.from_env()
        client.containers.run(repository_name, name=container_name, detach=True, network_mode='host', restart_policy={"Name": "always"})
        COMPONENTUPDATE.app.alert('Web application updated')

def main():
    if COMPONENTUPDATE.app.isrunnow:
        doupdateweb('updateweb')
        COMPONENTUPDATE.app.shutdown()
    else:
        COMPONENTUPDATE.listeningqueue = COMPONENTUPDATE.app.subscribe(QueueName.Q_UPDATEWEB, when_updateweb)
        COMPONENTUPDATE.listen()

if __name__ == "__main__":
    main()
