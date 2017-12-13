import json
import unittest
from .test_data_loader import *
from app.repository.MovieRepository import MovieRepository

CONNECTION_STR = {"DB_HOST": "localhost", "DB_PORT": 27017, "DB_NAME": "whatflix_test"}


class MovieRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_movies()
        load_users()

    def test_movies_for_all_users(self):
        self.connection_string = CONNECTION_STR
        repository = MovieRepository(self.connection_string)
        result = list(repository.get_movies())

        self.assertEqual(4, len(result), "Error")

    def test_movies_for_user_without_any_preferences(self):
        repository = MovieRepository(CONNECTION_STR)
        result = list(repository.get_movies())
        actual = [x for x in result if x["user"] == "1"][0]
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(user="1", movies=[
            "Movie 1",
            "Movie 2",
            "Movie 3"
        ]), actual, "Error")

    def test_movies_for_user_with_only_lang_preferences(self):
        repository = MovieRepository(CONNECTION_STR)
        result = list(repository.get_movies())
        actual = [x for x in result if x["user"] == "2"][0]
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(movies=[
            "Movie 1",
            "Movie 2",
            "Movie 3"
        ], user="2"), actual, "Error")

    def test_movies_for_user_with_only_actor_preferences(self):
        repository = MovieRepository(CONNECTION_STR)
        result = list(repository.get_movies())
        actual = [x for x in result if x["user"] == "3"][0]
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(movies=[
            "Movie 1",
            "Movie 3"
        ], user="3"), actual, "Error")

    def test_movies_for_user_with_only_director_preferences(self):
        repository = MovieRepository(CONNECTION_STR)
        result = list(repository.get_movies())
        actual = [x for x in result if x["user"] == "4"][0]
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(movies=[
            "Movie 1",
            "Movie 3"
        ], user="4"), actual, "Error")

    def test_movies_for_user_without_preferences_and_no_search_criteria(self):
        repository = MovieRepository(CONNECTION_STR)
        actual = repository.get_movies_for_user("1", [])
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(recommendations_by_search_and_preference=[
            "Movie 1",
            "Movie 2",
            "Movie 3",
            "Movie 4"
        ], recommendations_by_search=[]), actual, "Error")

    def test_movies_for_user_without_preferences_and_with_single_search_criteria(self):
        repository = MovieRepository(CONNECTION_STR)
        actual = repository.get_movies_for_user("1", ["1"])
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(recommendations_by_search_and_preference=[
            "Movie 1",
            "Movie 3"
        ], recommendations_by_search=[]), actual, "Error")

    def test_movies_for_user_without_preferences_and_with_multiple_search_criteria(self):
        repository = MovieRepository(CONNECTION_STR)
        actual = repository.get_movies_for_user("1", ["actor 1", "actor 2"])
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(recommendations_by_search_and_preference=[
            "Movie 1",
            "Movie 3"
        ], recommendations_by_search=[]), actual, "Error")

    def test_movies_for_user_with_case_insensitive_search_criteria(self):
        repository = MovieRepository(CONNECTION_STR)
        actual = repository.get_movies_for_user("1", ["ACTor 2"])
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(recommendations_by_search_and_preference=[
            "Movie 1"
        ], recommendations_by_search=[]), actual, "Error")

    def test_movies_for_user_with_preferences_and_search_criteria(self):
        repository = MovieRepository(CONNECTION_STR)
        actual = repository.get_movies_for_user("3", ["actor 2"])
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(recommendations_by_search_and_preference=[
            "Movie 1"
        ], recommendations_by_search=[]), actual, "Error")

    def test_movies_for_user_with_preferences_and_no_matching_search_criteria(self):
        repository = MovieRepository(CONNECTION_STR)
        actual = repository.get_movies_for_user("3", ["Movie 4"])
        print(json.dumps(actual, indent=4))

        self.assertEqual(dict(recommendations_by_search_and_preference=[],
                              recommendations_by_search=["Movie 4"]), actual, "Error")

    @classmethod
    def tearDownClass(cls):
        delete_movies()
        delete_users()
