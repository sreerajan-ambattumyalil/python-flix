from app.etl.movie_parser import parse_movies
from pymodm import connect
from app.model.Movie import Movie
from app.model.User import User
from app.config.config import *
from app.etl.user_parser import parse_users


def execute():
    etl_config = EtlConfig()
    USER_PREFERENCES_FILE_NAME = etl_config.USER_PREFERENCES_FILE_NAME
    FILE_PATH = etl_config.FILE_PATH
    MOVIES_FILE_NAME = etl_config.MOVIES_FILE_NAME
    MOVIES_CREDITS_FILE_NAME = etl_config.MOVIES_CREDITS_FILE_NAME
    LANGUAGE_CODES_FILE_NAME = etl_config.LANGUAGE_CODES_FILE_NAME

    connect(""
            "mongodb://"
            + etl_config.DB_HOST
            + ":"
            + str(etl_config.DB_PORT)
            + "/"
            + etl_config.DB_NAME,
            etl_config.DB_CONNECTION)

    User.objects.delete()
    Movie.objects.delete()

    movies = parse_movies(
        FILE_PATH,
        MOVIES_FILE_NAME,
        LANGUAGE_CODES_FILE_NAME,
        MOVIES_CREDITS_FILE_NAME
    )
    Movie.objects.bulk_create(movies)

    users = parse_users(
        FILE_PATH,
        USER_PREFERENCES_FILE_NAME
    )
    User.objects.bulk_create(users)



if __name__ == '__main__':
    execute()

