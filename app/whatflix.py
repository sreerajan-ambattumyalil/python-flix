from bson import json_util
from flask import Flask
from flask import Response
from flask import request
import logging
import traceback

from .config.config import load_config
from .repository.MovieRepository import MovieRepository
from .repository.UserNotFoundException import UserNotFoundException

app = Flask(__name__)
logging.basicConfig(filename='movies_app.log', level=logging.INFO)

app.config.from_object(load_config())


@app.route('/movies/heartbeat')
def heart_beat():
    return Response(
        json_util.dumps({'Message': "I am alive!"}),
        mimetype='application/json',
        status=200
    )


@app.route('/movies/users')
def get_movies():
    try:
        repository = MovieRepository(app.config)
        movies = repository.get_movies()

        return Response(
            json_util.dumps({'data': movies}),
            mimetype='application/json',
            status=200
        )

    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        return Response(
            json_util.dumps({'error': "Something unexpected happened!"}),
            mimetype='application/json',
            status=500
        )


@app.route('/movies/user/<user_id>/search')
def get_movies_for_user(user_id):
    try:
        search_text = request.args.get("text")
        search_terms = [] if search_text == [] or search_text is None else search_text.split(",")

        recommendations = MovieRepository(app.config).get_movies_for_user(user_id=user_id, search_terms=search_terms)

        return Response(
            json_util.dumps({'data': recommendations}),
            mimetype='application/json',
            status=200
        )

    except UserNotFoundException as ue:
        message = "User not found!"
        logging.error(message, user_id)
        return Response(
            json_util.dumps({'error': message, "user_id": user_id}),
            mimetype='application/json',
            status=404
        )

    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        return Response(
            json_util.dumps({'error': "Something unexpected happened!"}),
            mimetype='application/json',
            status=500
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
