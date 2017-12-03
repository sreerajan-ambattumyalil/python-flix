from pymodm import MongoModel, fields
from pymongo import WriteConcern
from config.config import config


class User(MongoModel):

    id = fields.CharField(primary_key=True)
    preferred_languages = fields.ListField()
    favourite_actors = fields.ListField()
    favourite_directors = fields.ListField()

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias= config.mongo.connection