'''checks for web update'''
import datetime
import docker
from helpers.queuehelper import QueueName
from fcmapp import Component

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
    print(msg)
    cli = docker.client.APIClient()
    containerName = COMPONENTUPDATE.app.configuration('update.fullcycleweb.name.container')
    configLocal = cli.inspect_container(containerName)
    containerid = configLocal['Id']
    createdLocal = configLocal['Created']
    createdLocalTime = datetime.datetime.strptime(createdLocal[:createdLocal.find('.')], "%Y-%m-%dT%H:%M:%S")
    print('Local Container', containerid, createdLocalTime)
    repositoryName = COMPONENTUPDATE.app.configuration('update.fullcycleweb.name.repository')
    configHub = cli.inspect_container(containerid)
    createdHub = configHub['Created']
    createdHubTime = datetime.datetime.strptime(createdHub[:createdHub.find('.')], "%Y-%m-%dT%H:%M:%S")
    print('Remote Repository', createdHubTime)
    if createdLocalTime < createdHubTime:
       print('Web application needs update')
       #docker stop
       cli.stop(containerName)
       #docker rm
       cli.remove_container(containerName)
       #docker pull
       cli.pull(repositoryName)
       #docker run --name fullcycleweb -d --network=host --restart unless-stopped fullcycle/web
       client = docker.from_env()
       client.containers.run(repositoryName, name=containerName, detach=True, network_mode='host', restart_policy={"Name": "always"} )
    else:
       print('Web application is up to date')

def main():
    if COMPONENTUPDATE.app.isrunnow:
        doupdateweb('updateweb')
        COMPONENTUPDATE.app.shutdown()
    else:
        COMPONENTUPDATE.listeningqueue = COMPONENTUPDATE.app.listen_to_broadcast(QueueName.Q_UPDATEWEB, when_updateweb)

if __name__ == "__main__":
    main()

