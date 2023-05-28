from json import dump, load

class Manager(object):
    def __init__(self):
        pass

    def load_settings(self) -> object:
        with open('assets/settings.json', 'rb') as file:
            return load(file)

    def update_settings(self, settings: object) -> None:
        with open('assets/settings.json', 'w') as file:
            dump(settings, file, indent=2)
            
    