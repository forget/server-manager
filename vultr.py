from requests import Session
from manager import Manager
from time import sleep
from threading import Thread

class VULTR:
    def __init__(self):
        self.session = Session()
        self.vultr_api_key = "" # your api key
        self.servers = 1 # servers you need
        self.label = "me" # the name of your instance
        
        self.active_servers = []
                       
        self.init()
       
    def create_instance(self, index):
        try:
            data = {
                'region': 'sjc',
                'plan': 'vhf-1c-1gb',
                'os_id': 387, # Ubuntu
                'label': f'{self.label} [#{index}]'
            }
            
            headers = {
                'Authorization': 'Bearer ' + str(self.vultr_api_key),
                'Content-Type': 'application/json'
            }
            
            instance = self.session.post('https://api.vultr.com/v2/instances', json=data, headers=headers).json()['instance']
            
            password, instance_id = instance['default_password'], instance['id']
            
            while True:
                try:
                    json_response = self.session.get(f'https://api.vultr.com/v2/instances/{instance_id}', headers=headers).json()['instance']
                except:
                    pass
                
                if json_response['status'] == 'active':
                    ip = json_response['main_ip']
                    break
            return ip, password, instance_id
        except:
            return False
    
    def delete_instance(self, instance_id):
        headers = {
            'Authorization': 'Bearer ' + str(self.vultr_api_key)
        }
        while 1:
            try:
                status_code = self.session.delete(f'https://api.vultr.com/v2/instances/{instance_id}', headers=headers).status_code
            except:
                pass
            
            if status_code == 204:
                return True
            else:
                return False
            
       
    def set_console_info(self):
        while True:
            print(f'[VULTR] Servers: {self.servers} | Active Servers: {len(self.active_servers)}', end="\r")

    def main(self, index):
        while True:
            while 1:
                data = self.create_instance(index)
                if not data == False:
                    ip, password, instance_id = data
                    break
            
            # Check if the server has been deployed properly
            if not len(instance_id) < 0:
                print(f'[#{index}] Successfully deployed {ip}!')
            else:
                sleep(60)
                return self.delete_instance(instance_id)
            
            sleep(90) # Give it some time to set up
            
            server = Manager(index, ip, password)
            
            try:
                # Connect to the server
                while 1:
                    if server.connect():
                        print(f'[#{index}] Successfully connected to {ip}!')
                        break  
                    
                sleep(10)
                
                # Upload files onto the server
                while 1:
                    if server.upload_files():
                        print(f"[#{index}] Files have been uploaded to {ip}!")
                        break
    
                # Disconnect from the server
                while 1:
                    if server.disconnect():
                        print(f"[#{index}] Successfully disconnected from {ip}!")
                        break
                   
                # Add your task here and let it sleep for however long you feel necessary
                sleep(28800)
                
                # Download the files onto local PC
                while 1:
                    if server.download_files():
                        print(f"[#{index}] Successfully downloaded files from {ip}!")
                        break
                
                sleep(5)
                
                # Now, after we have done what we needed, we simply get rid of the instance.
                while 1:
                    if self.delete_instance(instance_id):
                        print(f'[#{index}] Successfully destroyed {instance_id}!')
                        break
                
                # Remove the server from the active pool list
                self.active_servers.remove(instance_id)
            except KeyboardInterrupt:
                return self.delete_instance(instance_id)
    
    def init(self):
        print('Vultr Deployer started!')
        
        for x in range(int(self.servers)):
            Thread(target=self.main, args=(x,)).start()
           
if __name__ == '__main__':
    VULTR()
