'''ssh client
use with, or finally close
See
https://daanlenaerts.com/blog/2016/07/01/python-and-ssh-paramiko-shell/
https://stackoverflow.com/questions/39606573/unable-to-kill-python-script
'''
import threading
import paramiko

class Ssh:
    '''communicate with miner through ssh'''
    shell = None
    client = None
    transport = None
    closed = False

    strdata = ''
    alldata = ''

    def __init__(self, address, username='root', password='admin', port=22):
        print("Connecting to server on ip {0}:{1}".format(address, port))
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, port=port, username=username, password=password, look_for_keys=False)
        print("Connection created")
        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    def exec_command(self, command):
        '''use this if you only need to run ONE command
        This is the preferred way to communicate with miner
        returns a list of lines as the response to the command
        '''
        _, stdout_, _ = self.client.exec_command(command)
        #this will make it block until response is received
        stdout_.channel.recv_exit_status()
        return stdout_.readlines()

    def close_connection(self):
        '''close the ssh connection'''
        self.thread.join(timeout=10)
        if self.client != None:
            self.client.close()
            if self.transport is not None:
                self.transport.close()
        self.closed = True

    def open_shell(self):
        '''open shell command to run a series of command
        try to avoid if possible
        may have some async/threading issues
        '''
        self.shell = self.client.invoke_shell()

    def send_shell(self, command):
        '''send command to shell'''
        if self.shell:
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")

    def process(self):
        '''process the commands'''
        while self.closed is False:
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
        print("ssh process closed")

    def get(self, remotefile, localfile):
        #ftp_client=self.client.open_sftp()
        #ftp_client.get(remotefile, localfile)
        #ftp_client.close()
        pass

    def put(self, localfile, remotefile):
        transport = self.client.get_transport()
        with transport.open_channel(kind='session') as channel:
            with open(localfile, 'rb') as config_file:
                file_data = config_file.read()
            channel.exec_command('cat > {0}'.format(remotefile))
            channel.sendall(file_data)
