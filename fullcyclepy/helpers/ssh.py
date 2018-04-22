'''ssg client'''
import threading
import paramiko

class Ssh:
    '''communicate with miner through ssh'''
    shell = None
    client = None
    transport = None

    strdata = ''
    alldata = ''

    def __init__(self, address, username='root', password='admin', port=22):
        print("Connecting to server on ip {0}:{1}".format(address, port))
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, port=port, username=username, password=password, look_for_keys=False)
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()

    def close_connection(self):
        '''close the ssh connection'''
        if self.client != None:
            self.client.close()
            if self.transport is not None:
                self.transport.close()

    def open_shell(self):
        '''open shell command'''
        self.shell = self.client.invoke_shell()

    def send_shell(self, command):
        '''send command to shell'''
        if self.shell:
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")

    def process(self):
        '''process the commands'''
        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                print(strdata, end="")
                if strdata.endswith("$ "):
                    print("\n$ ", end="")
