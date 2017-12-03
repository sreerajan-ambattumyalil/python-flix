from etl.movie_loader import load_movies
from pymodm import connect
from model.Movie import Movie
from model.User import User
from config.config import config
from etl.user_loader import load_users

USER_PREFERENCES_FILE_NAME = "user_preferences.json"
FILE_PATH = "./data"
MOVIES_FILE_NAME = "tmdb_5000_movies.csv"
MOVIES_CREDITS_FILE_NAME = "tmdb_5000_credits.csv"
LANGUAGE_CODES_FILE_NAME = "language_codes.csv"

connect("mongodb://" + config.mongo.host + ":" + config.mongo.port + "/" + config.mongo.db, config.mongo.connection)

movies = load_movies(
    FILE_PATH,
    MOVIES_FILE_NAME,
    LANGUAGE_CODES_FILE_NAME,
    MOVIES_CREDITS_FILE_NAME
)

Movie.objects.bulk_create(movies)


users = load_users(
    FILE_PATH,
    USER_PREFERENCES_FILE_NAME
)

User.objects.bulk_create(users)
