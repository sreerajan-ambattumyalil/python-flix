from app.model.Movie import Movie
from app.model.User import User
from pymodm import connect
from pymongo import MongoClient

connect(""
        "mongodb://"
        + "localhost"
        + ":"
        + "27017"
        + "/"
        + "whatflix_test",
        "whatflix")


def load_movies():
    delete_movies()

    movies = [
        Movie(
            1,
            title="Movie 1",
            actors=["Actor 1", "Actor 2", "Actor 3"],
            directors=["Director 1"],
            languages=["lan 1", "lan 2"]
        ),
        Movie(
            2,
            title="Movie 2",
            actors=["Actor 4, Actor 5", "Actor 6"],
            directors=["Director 2"],
            languages=["lan 3"]
        ),
        Movie(
            3,
            title="Movie 3",
            actors=["Actor 1", "Actor 3"],
            directors=["Director 1"],
            languages=["lan 1"]
        ),
        Movie(
            4,
            title="Movie 4",
            actors=["Actor 5, Actor 6"],
            directors=["Director 2"],
            languages=["lan 4"]
        )
    ]

    movie_ids = Movie.objects.bulk_create(movies)
    print("Created movies : ", movie_ids)


def delete_movies():
    Movie.objects.delete()


def load_users():
    delete_users()

    user_without_preferences = \
        User(1,
             preferred_languages=[],
             favourite_actors=[],
             favourite_directors=[])
    user_with_lang_pref = \
        User(2,
             preferred_languages=["lan 1", "lan 3"],
             favourite_actors=[],
             favourite_directors=[])

    user_with_actor_pref = \
        User(3,
             preferred_languages=[],
             favourite_actors=["Actor 1"],
             favourite_directors=[])

    user_with_director_pref = \
        User(4,
             preferred_languages=[],
             favourite_actors=[],
             favourite_directors=["Director 1"])

    users = [
        user_without_preferences,
        user_with_actor_pref,
        user_with_director_pref,
        user_with_lang_pref
    ]

    user_ids = User.objects.bulk_create(users)
    print("Created users : ", user_ids)


def delete_users():
    User.objects.delete()