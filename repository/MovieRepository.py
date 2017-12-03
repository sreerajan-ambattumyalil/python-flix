import re

from pymongo import ASCENDING
from pymongo import MongoClient
from .UserNotFoundException import UserNotFoundException
from config.config import config


class MovieRepository():

    def __init__(self):
        client = MongoClient(config.mongo.host, config.mongo.port)
        self.movie_collection = client[config.mongo.db].movie
        self.user_collection = client[config.mongo.db].user

    def get_movies_for_user(self, user_id, search_terms):
        user_preferences = self.user_collection.find_one(
            {"_id": user_id},
            {"_id": 0, "favourite_actors": 1, "favourite_directors": 1,"preferred_languages": 1, }
        )

        if user_preferences is None:
            raise UserNotFoundException(user_id)

        movies =\
            self.populate_movies(user_preferences, "favourite_actors", "actors", search_terms) +\
            self.populate_movies(user_preferences, "favourite_directors", "directors", search_terms) +\
            self.populate_movies(user_preferences, "preferred_languages", "languages", search_terms)

        return {
            "recommendations_by_preference" : list(set(map(lambda v: v["title"], movies))),
            "recommendations" : list(set(map(lambda v: v["title"], self.get_default_recommendations(search_terms)))) if not movies else []
        }

    def get_movies(self):
        filtered_on_actors = self.user_collection.aggregate(
            self.filter_pipeline_on("favourite_actors", "actors")
        )

        filtered_on_directors = self.user_collection.aggregate(
            self.filter_pipeline_on("favourite_directors", "directors")
        )

        filtered_on_languages = self.user_collection.aggregate(
            self.filter_pipeline_on("preferred_languages", "languages")
        )

        default_recommendations = self.no_preference_users()

        combined_result = {}

        self.accumulate_records(combined_result, filtered_on_actors)
        self.accumulate_records(combined_result, filtered_on_directors)
        self.accumulate_records(combined_result, filtered_on_languages)
        self.accumulate_records(combined_result, default_recommendations)

        return self.cleanse(combined_result)

    def no_preference_users(self):
        users_without_preferences = \
            list(
                map(
                    lambda rec: rec['_id'],
                    self.user_collection.find(
                        {
                            "$and": [
                                {
                                    "favourite_directors": {
                                        "$eq": []
                                    }
                                },
                                {
                                    "favourite_actors": {
                                        "$eq": []
                                    }
                                },
                                {
                                    "preferred_languages": {
                                        "$eq": []
                                    }
                                }
                            ]
                        },
                        {"_id": 1}
                    )
                )
            )
        default_movies = \
            list(
                map(
                    lambda rec: rec['title'],
                    self.movie_collection.aggregate(
                        [
                            {
                                "$sort": {
                                    "title": 1
                                }
                            },
                            {
                                "$limit": 3
                            },
                            {
                                "$project": {
                                    "_id": 0,
                                    "title": 1
                                }
                            }
                        ]
                    )
                )
            )
        default_recommendations = map(lambda k, v: {"user_id": k, "movies": v}, users_without_preferences,
                                      list(default_movies))
        return default_recommendations

    def filter_pipeline_on(self, local_field, foreign_field):
        return [
            self.match_on(local_field),
            self.lookup_on(local_field, foreign_field),
            self.project()
        ]

    def match_on(self, field="favourite_actors"):
        return {
            "$match": {
                "$and": [
                    {
                        field: {
                            "$ne": []
                        }
                    }
                ]
            }
        }

    def project(self):
        return {
            "$project": {
                "_id": 0,
                "user_id": "$_id",
                "movies": {
                    "$map": {
                        "input": "$result_set",
                        "as": "movie_details",
                        "in": "$$movie_details.title"
                    }
                }
            }
        }

    def lookup_on(self, local_field, foreign_field):
        return {
            "$lookup": {
                "from": "movie",
                "localField": local_field,
                "foreignField": foreign_field,
                "as": "result_set"
            }
        }

    def cleanse(self, combined_result):
        return map(lambda k, v: {"user": k, "movies": sorted(set(v))[0:3]}, combined_result.keys(),
                   combined_result.values())

    def accumulate_records(self, combined_result, input):
        for rec in input:
            user_id_ = rec["user_id"]
            if user_id_ in combined_result:
                for movie in rec["movies"]:
                    combined_result[user_id_].append(movie)
            else:
                combined_result[user_id_] = rec["movies"]


    def get_default_recommendations(self, search_terms):
        self.movie_collection.find(
            {
                "$or": [
                    {
                        "actors": {
                            "$in": self.search_function(search_terms)
                        }
                    },
                    {
                        "directors": {
                            "$in": self.search_function(search_terms)
                        }
                    },
                    {
                        "languages": {
                            "$in": self.search_function(search_terms)
                        }
                    }
                ]
            }
        )

    def populate_movies(self, user_preferences, foreign_field, local_field, search_terms):

        if user_preferences[foreign_field]:
            result = self.movie_collection.find(
                {
                    "$and": [
                        {
                            local_field: {
                                "$in": user_preferences[foreign_field]
                            }
                        },
                        {
                            local_field: {
                                "$in": self.search_function(search_terms)
                            }
                        }
                    ]
                },
                {
                    "_id": 0,
                    "title": 1
                }
            )
            return list(result.sort("title", ASCENDING))
        []

    def search_function(self, search_terms):
        return list(map(lambda s: re.compile(s, re.IGNORECASE), search_terms)) if search_terms != [] else [re.compile(".*")]