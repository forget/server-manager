from paramiko import SSHClient, AutoAddPolicy
from time import sleep

import os

class Assistant(object):
    def __init__(self, server_index: int, server_ip: str, server_password: str):        
        self.server_index: int = server_index
        self.server_ip: str = server_ip
        self.server_pwd: str = server_password

        self.sftp = None
        self.ssh: SSHClient = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        
    def connect(self):
        try:
            self.ssh.connect(self.server_ip, username = "root", password = self.server_pwd)
            return True
        except:
            print(f"[#{self.server_index}] Unable to connect, sleeping for 15 seconds...")
            sleep(15)
            return False
    
    def disconnect(self):
        try:
            self.ssh.close()
            self.sftp.close()
            return True
        except:
            return False
        
    def install_dependencies(self):
        try:
            stdin, stdout, stderr = self.ssh.exec_command('sudo apt-get upgrade -y && sudo apt install python3-pip')           
            if not stdout.channel.recv_exit_status():
                return True
        except:
            print(f"[#{self.server_index}] Unable to install dependencies, sleeping for 15 seconds...")
            sleep(15)
            return False
            
    def upload_files(self):
        try:
            local_files = [f for f in os.listdir(f'files/{self.server_index}') if os.path.isfile(os.path.join(f'files/{self.server_index}', f))]
            dirs = [f for f in os.listdir(f'files/{self.server_index}') if os.path.isdir(os.path.join(f'files/{self.server_index}', f))]

            self.sftp = self.ssh.open_sftp()
            sleep(5)
            
            self.sftp.mkdir('remote_files')
            for file in local_files:
                self.sftp.put(os.path.abspath(os.path.join(f'files/{self.server_index}/{file}')), f'remote_files/{file}')
            for d in dirs:
                if d != "__pycache__":
                    self.sftp.mkdir(f'remote_files/{d}')
                    for file in os.listdir(f'files/{self.server_index}/{d}'):
                        self.sftp.put(os.path.abspath(os.path.join(f'files/{self.server_index}/{d}/{file}')), f'remote_files/{d}/{file}')
            return True
        except:
            print(f"[#{self.server_index}] Unable to upload files, sleeping for 5 seconds...")
            sleep(5)
            return False
            
    def download_files(self):
        while True:
            try:
                # Conect to the server
                self.ssh.connect(self.ip, 22, 'root', self.password)
                break
            except:
                print(f"[#{self.server_index}] Unable to connect, sleeping for 15 seconds...")
                sleep(15)

        while 1:
            try:
                self.sftp = self.ssh.open_sftp()
                
                # SERVERS DIR, LOCAL DIR
                self.sftp.get(f'x', 'x')
                return True
            except:
                return False
