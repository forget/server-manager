from json import dumps
from copy import deepcopy
from requests import post
from logging import info, warning

from datetime import datetime
from random import randint

from library.manager import Manager

class Logger(object):
    def __init__(self) -> None:
        self.manager: object = Manager()
                        
        self.base_webhook: object = {
            'embeds': [{
                "title": None,
                "color": None,
                "description": None,
                'footer': {
                    'text': None,
                    "icon_url": None
                }
            }]
        }
        
        self.settings: object = self.manager.load_settings()
        self.send_webhooks: bool = self.settings['send_webhooks']
        self.webhook_url: str = self.settings['webhook_url']
        self.operator: str = self.settings["current_operator"]
        
    def log(self, message: str) -> None:       
        webhook = deepcopy(self.base_webhook)
        webhook['embeds'][0]['color'] = randint(1, 16777214)
        webhook['embeds'][0]['title'] = f"Notification: {self.operator}"
        webhook['embeds'][0]['description'] = message
        webhook['embeds'][0]['footer']['text'] = f'Timestamp: {datetime.utcnow()}'

        
        if self.send_webhooks is True:
            try:
                post(self.webhook_url, headers={"Content-Type": "application/json"}, data=dumps(webhook))
            except:
                pass     
        info(message)

    def warning(self, message: str) -> None:        
        webhook = deepcopy(self.base_webhook)
        webhook['embeds'][0]['color'] = randint(1, 16777214)
        webhook['embeds'][0]['title'] = f"Warning: {self.operator}"
        webhook['embeds'][0]['description'] = message
        webhook['embeds'][0]['footer']['text'] = f'Timestamp: {datetime.utcnow()}'

        if self.send_webhooks is True:
            try:
                post(self.webhook_url, headers={"Content-Type": "application/json"}, data=dumps(webhook))
            except:
                pass          
        warning(message)
        