import json
import os
from collections import namedtuple
import logging

env = os.getenv("ENV", "dev")
config = {}

with open('./config/config.' + env + ".json") as config_json_file:
    config = json.load(
        config_json_file,
        object_hook=lambda dict: namedtuple('Config', dict.keys())(*dict.values()))


class Config:
    DEBUG=False
    TESTING=False
    DB_HOST="localhost"
    DB_PORT = 27017
    DB_NAME="whatflix_default"
    DB_CONNECTION="whatflix"

class EtlConfig(Config):
    DB_NAME = "whatflix"
    USER_PREFERENCES_FILE_NAME = "user_preferences.json"
    FILE_PATH = "./data"
    MOVIES_FILE_NAME = "tmdb_5000_movies.csv"
    MOVIES_CREDITS_FILE_NAME = "tmdb_5000_credits.csv"
    LANGUAGE_CODES_FILE_NAME = "language_codes.csv"

class ProductionConfig(Config):
    DB_NAME = "whatflix"

class DevelopmentConfig(Config):
    DB_NAME = "whatflix"

class TestingConfig(Config):
    DB_NAME = "whatflix_test"


def load_config():
    env = os.getenv("ENV", "dev")
    if env == "dev":
        logging.info("Loading development config")
        return DevelopmentConfig
    elif env == "testing":
        logging.info("Loading testing config")
        return TestingConfig
    else:
        logging.info("Loading prod config")
        return ProductionConfig
