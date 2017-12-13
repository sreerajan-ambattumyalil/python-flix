import re

from pymongo import ASCENDING
from pymongo import MongoClient
from .UserNotFoundException import UserNotFoundException


def project():
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


def match_on(field):
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


def lookup_on(local_field, foreign_field):
    return {
        "$lookup": {
            "from": "movie",
            "localField": local_field,
            "foreignField": foreign_field,
            "as": "result_set"
        }
    }


def filter_pipeline_on(local_field, foreign_field):
    query = [
        match_on(local_field),
        lookup_on(local_field, foreign_field),
        project()]
    return query


def cleanse(combined_result):
    return map(lambda k, v: {"user": k, "movies": sorted(set(v))[0:3]}, combined_result.keys(),
               combined_result.values())


def accumulate_records(combined_result, input):
    for rec in input:
        user_id_ = rec["user_id"]
        if user_id_ in combined_result:
            for movie in rec["movies"]:
                combined_result[user_id_].append(movie)
        else:
            combined_result[user_id_] = rec["movies"]


def search_function(search_terms):
    reg_ex =\
        re.compile("|".join(search_terms), re.IGNORECASE)\
        if search_terms != [] else re.compile(".*")
    return reg_ex


class MovieRepository():

    def __init__(self, app_config):
        client = MongoClient(app_config["DB_HOST"], app_config["DB_PORT"])
        self.movie_collection = client[app_config["DB_NAME"]].movie
        self.user_collection = client[app_config["DB_NAME"]].user

    def get_movies_for_user(self, user_id: str, search_terms: list):
        user_preferences = self.user_collection.find_one(
            {"_id": user_id},
            {"_id": 0, "favourite_actors": 1, "favourite_directors": 1, "preferred_languages": 1, }
        )

        if user_preferences is None:
            raise UserNotFoundException(user_id)

        movies_by_actors = self.find_movies(user_preferences, "favourite_actors", "actors", search_terms)
        movies_by_directors = self.find_movies(user_preferences, "favourite_directors", "directors", search_terms)
        movies_by_languages = self.find_movies(user_preferences, "preferred_languages", "languages", search_terms)
        # movies_by_title = self.find_movies(user_preferences, "title", "title", search_terms)

        movies = movies_by_actors + movies_by_directors + movies_by_languages

        return dict(
            recommendations_by_search_and_preference=sorted(list(set(map(lambda v: v["title"], movies)))),
            recommendations_by_search=list(set(map(lambda v: v["title"], self.get_default_recommendations(search_terms)))) if not movies else []
        )

    def get_movies(self):
        filtered_on_actors = self.user_collection.aggregate(
            filter_pipeline_on("favourite_actors", "actors")
        )

        filtered_on_directors = self.user_collection.aggregate(
            filter_pipeline_on("favourite_directors", "directors")
        )

        filtered_on_languages = self.user_collection.aggregate(
            filter_pipeline_on("preferred_languages", "languages")
        )

        default_recommendations = self.no_preference_users()

        combined_result = {}

        accumulate_records(combined_result, filtered_on_actors)
        accumulate_records(combined_result, filtered_on_directors)
        accumulate_records(combined_result, filtered_on_languages)
        accumulate_records(combined_result, default_recommendations)

        return cleanse(combined_result)

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

        default_recommendations = []
        for user_id in users_without_preferences:
            default_recommendations.append({
                "user_id": user_id,
                "movies": default_movies
            })

        return default_recommendations

    def get_default_recommendations(self, search_terms):
        return self.movie_collection.find(
            {
                "$or": [
                    {
                        "actors":  search_function(search_terms)
                    },
                    {
                        "directors": search_function(search_terms)
                    },
                    {
                        "languages": search_function(search_terms)
                    },
                    {
                        "title": search_function(search_terms)
                    }
                ]
            }
        )

    def find_movies(self, user_preferences, foreign_field, local_field, search_terms):

        search_query = {local_field : search_function(search_terms)}
        if foreign_field in user_preferences and user_preferences[foreign_field]:
            search_query =\
                {
                    "$and" : [
                        {
                            local_field: {
                                "$in": user_preferences[foreign_field]
                            }
                        },
                        search_query
                    ]
                }

        result = self.movie_collection.find(
             search_query,
            {
                "_id": 0,
                "title": 1
            }
        )
        return list(result.sort("title", ASCENDING))
