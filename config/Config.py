import json
import os

class Config:

    configPath = os.getcwd() + '/config/config.json'

    def get(self, collection, key):
        with open(self.configPath) as my_file:
            data = my_file.read().replace('\n', '')
            config = json.loads(data)
            return config[collection][key]

