from pymodm import MongoModel, fields
from pymongo import WriteConcern


class Movie(MongoModel):

    id = fields.CharField(primary_key=True)
    title = fields.CharField()
    actors = fields.ListField()
    directors = fields.ListField()
    languages = fields.ListField()

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias= "whatflix"