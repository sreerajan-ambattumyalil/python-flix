# ETL module for loading movies to the database
import csv
import logging
import json
import traceback
import os
from app.model.Movie import Movie

from app.etl.constants import *


def __add_languages(language_codes, spoken_languages):
    languages = []
    for language in json.loads(spoken_languages):
        try:
            iso_code = language[LANGUAGE_CODE_ISO]
            if not language_codes.__contains__(iso_code):
                language = UN_KNOWN
            else:
                language = language_codes[iso_code]
            languages.append(language)
        except:
            logging.error("Error parsing language")
            logging.error(language)
            raise
    return languages;


def __load_langauges(path, file_name):

    language_codes = {}

    with open(os.path.join(path, file_name)) as languages_file:
        languages_reader = csv.DictReader(languages_file, delimiter=DELIMITER)
        for row in languages_reader:
            language_codes[row[LANGUAGE_CODE_FIELD]] = row[LANGUAGE_FIELD]

    return language_codes


def __add_actors_and_directors(movies, path, file_name):
    with open(os.path.join(path, file_name)) as movies_credits_file:
        movies_credits_reader = csv.DictReader(movies_credits_file, delimiter=DELIMITER)
        for row in movies_credits_reader:
            [movie for movie in
             movies if
             movie[ID] == row[MOVIE_ID]][0][DIRECTORS] = [crew["name"] for crew in
                                                          json.loads(row[CREW]) if
                                                          crew["job"] == "Director"]
            [movie for movie in
             movies if
             movie[ID] == row[MOVIE_ID]][0][ACTORS] = [cast["name"] for cast in
                                                       json.loads(row["cast"]) if
                                                       cast["order"] in ACTOR_ORDER_CHOICES]


def __load_basic_movie_data(path, file_name, langauge_codes):
    movies = []
    with open(os.path.join(path, file_name)) as movies_file:
        movies_reader = csv.DictReader(movies_file, delimiter=DELIMITER)
        for row in movies_reader:
            movie = {}
            movie[MOVIE_TITLE_FIELD] = row[MOVIE_TITLE_FIELD]
            movie[ID] = row[ID]
            movie[LANGUAGES_FIELD] = __add_languages(langauge_codes, row[SPOKEN_LANGUAGES_FIELD])
            movies.append(movie)
    return movies


def parse_movies(
        file_path,
        movies_file_name,
        language_codes_file_name,
        movies_credits_file_name):

    logging.basicConfig(filename='movies_etl.log', level=logging.INFO)

    try:
        movies = []

        langauge_codes = __load_langauges(
            file_path,
            language_codes_file_name
        )

        movies_data = __load_basic_movie_data(
            file_path,
            movies_file_name,
            langauge_codes
        )

        __add_actors_and_directors(
            movies_data,
            file_path,
            movies_credits_file_name
        )

        for movie in movies_data:
            movies.append(Movie(
                movie[ID],
                title = movie[MOVIE_TITLE_FIELD],
                directors = movie[DIRECTORS],
                actors = movie[ACTORS],
                languages = movie[LANGUAGES_FIELD]
            ))

        logging.info("Loaded movies!")

        return movies

    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
    finally:
        logging.shutdown()


if __name__ == "__main__":
    parse_movies()