import json
import os
from collections import namedtuple

env = os.getenv("ENV", "dev")
config = {}

with open('./config/config.' + env + ".json") as config_json_file:
    config = json.load(
        config_json_file,
        object_hook=lambda dict: namedtuple('Config', dict.keys())(*dict.values()))