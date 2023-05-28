# VULTR API: https://www.vultr.com/api/
# Creator: https://github.com/forget/

from requests import Session
from threading import Thread

from library.manager import Manager
from library.logger import Logger
from library.assistant import Assistant

from logging import INFO, basicConfig
from time import sleep

basicConfig(
    level=INFO, 
    format='[%(levelname)s] [%(asctime)s] %(message)s', 
    datefmt='%b %d | %H:%M', 
    filename='deployment.log',
)

class VULTR(object):
    def __init__(self):
        self.session: Session = Session()
        self.manager: Manager = Manager()
        self.logger: Logger = Logger()
        
        self.settings: object = self.manager.load_settings()
        self.vultr_api_key: str = self.settings['vultr_api_key']
        self.operator: str = self.settings['current_operator']
        self.instances: int = self.settings['number_of_instances']
        self.name: str = self.settings['server_name']
        
        self.running: bool = True
                              
    def create_instance(self, index: int) -> bool:
            data = {
                'region': 'fra', # Frankfurt, Germany
                'plan': 'vhf-1c-1gb', # High frequency, 1 core 1 gb ram
                'os_id': 387, # Ubuntu / 244 Debian
                'label': '%s [#%s]' % (self.name, index)
            }
            
            headers = {
                'Authorization': 'Bearer ' + str(self.vultr_api_key),
                'Content-Type': 'application/json'
            }
            
            try:
                instance = self.session.post(
                    'https://api.vultr.com/v2/instances', 
                    json=data, headers=headers
                ).json()['instance']
                
                password: str = instance['default_password']
                instance_id: str = instance['id']
            except:
                return False
            
            while True:
                sleep(5)
                
                try:
                    json_response = self.session.get(
                        f'https://api.vultr.com/v2/instances/{instance_id}', 
                        headers=headers
                    ).json()['instance']
                    
                    if json_response['status'] == 'active':
                        ip: str = json_response['main_ip']
                        break
                except:
                    continue
            return ip, password, instance_id
    
    def delete_instance(self, instance_id: int) -> bool:
        headers = {
            'Authorization': 'Bearer ' + str(self.vultr_api_key)
        }
        
        while 1:
            sleep(10)
            try:
                return self.session.delete(
                    f'https://api.vultr.com/v2/instances/{instance_id}', 
                    headers=headers
                ).status_code == 204
            except:
                continue
            
    def main(self, index: int):
        sleep(int(index) * 10) # Add some delay between the deployment of each server
        
        while (self.running):
            while 1:
                data = self.create_instance(index)
                
                if data is False:
                    self.logger.warning(f"# {index}: Failed to deploy an instance, sleeping and retrying...")
                    sleep(290)
                    return self.delete_instance(instance_id)

                ip, password, instance_id = data
                
                self.logger.log(f" #{index}: Successfully created an instance - {ip}!")
                break

            # Give the server some time to set up properly.                       
            sleep(300)
            
            session = Assistant(index, ip, password)
            
            try:
                # Connect to the actual instance.
                while 1:
                    if session.connect():
                        self.logger.log(f" #{index}: Successfully connected to {ip}!")
                        break  
                    
                sleep(10)
                
                # Install dependencies and python modules.
                while 1:
                    if session.install_dependencies():
                        self.logger.log(f" #{index}: Successfully installed dependencies on {ip}!")
                        break
                
                sleep(5)
                
                # Upload our local files onto the server.
                while 1:
                    if session.upload_files():
                        self.logger.log(f" #{index}: Files have been uploaded to {ip}!")
                        break
                
                sleep(5)
                
                # You can add a function to start your task.
                
                # Disconnect from the server.
                while 1:
                    if session.disconnect():
                        self.logger.log(f" #{index}: Successfully disconnected from {ip}!")
                        break
                    
                # Sleep while our task is doing its job.
                sleep(28800) # 8 hours
                
                # Connect and save our files to local.
                while 1:
                    if session.download_files():
                        self.logger.log(f" #{index}: Successfully downloaded server files from {ip}!")
                        break
                
                sleep(5)
                
                # Now, after we have done what we needed, we simply get rid of the instance.
                while 1:
                    if self.delete_instance(instance_id):
                        self.logger.log(f" #{index}: Successfully destroyed our instance - {ip}!")
                        break
            except KeyboardInterrupt:
                self.running = False; return
    
    def init(self):
        print("Vultr Deployer Started!\n")
        
        for index in range(int(self.instances)):
            Thread(
                target=self.main, 
                args=(index,)
            ).start()
           
if __name__ == '__main__':
    VULTR().init()
