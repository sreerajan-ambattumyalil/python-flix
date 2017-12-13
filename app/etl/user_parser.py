import json
import os
from app.model.User import User


def parse_users(file_path, user_file_name):
    with open(os.path.join(file_path, user_file_name)) as user_file:

        user_data = json.load(user_file)
        users = []
        for x in user_data:
            users.append(list(
                map(
                    lambda k,v:
                    User(k,
                         preferred_languages = v['preferred_languages'],
                         favourite_actors = v['favourite_actors'],
                         favourite_directors = v['favourite_directors']
                         ), x.keys(), x.values()))[0])
            return users