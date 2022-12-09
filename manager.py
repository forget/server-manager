import paramiko, time, os

class Manager:
    def __init__(self, num, ip, password):
        self.ip = ip
        self.password = password
        self.num = num
              
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None

    def connect(self):
        try:
            self.ssh.connect(self.ip, username = "root", password = self.password)
            return True
        except:
            print(f"[#{self.num}] Unable to connect, sleeping for 15 seconds...")
            time.sleep(15)
            return False
    
    def disconnect(self):
        try:
            self.ssh.close()
            self.sftp.close()
            return True
        except:
            return False
            
    def upload_files(self):
        try:
            local_files = [f for f in os.listdir(f'server_files/{self.num}') if os.path.isfile(os.path.join(f'server_files/{self.num}', f))]
            dirs = [f for f in os.listdir(f'server_files/{self.num}') if os.path.isdir(os.path.join(f'server_files/{self.num}', f))]

            self.sftp = self.ssh.open_sftp()
            time.sleep(5)
            
            self.sftp.mkdir('files')
            for file in local_files:
                self.sftp.put(os.path.abspath(os.path.join(f'server_files/{self.num}/{file}')), f'files/{file}')
            for d in dirs:
                self.sftp.mkdir(f'files/{d}')
                for file in os.listdir(f'server_files/{self.num}/{d}'):
                    self.sftp.put(os.path.abspath(os.path.join(f'server_files/{self.num}/{d}/{file}')), f'files/{d}/{file}')
            return True
        except:
            print(f"[#{self.num}] Unable to upload files, sleeping for 5 seconds...")
            time.sleep(5)
            return False
            
    def download_files(self):
        while True:
            try:
                # Conect to the server
                self.ssh.connect(self.ip, 22, 'root', self.password)
                break
            except:
                print(f"[#{self.num}] Unable to connect, sleeping for 15 seconds...")
                time.sleep(15)

        while 1:
            try:
                self.sftp = self.ssh.open_sftp()
                
                # SERVERS DIR, LOCAL DIR
                self.sftp.get(f'x', 'x')
                return True
            except:
                return False
