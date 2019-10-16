# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask, Response, jsonify, request, json
import pandas as pd
import pickle
from google.cloud import storage
from os import environ
import os
import requests

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route("/api/hybrid/<userId>/<title>", methods=['GET'])
def make_hybrid(userId, title):
    df_movies = pd.read_csv("df_movies_final.csv")
    df_movies.set_index("movieId", inplace=True)

    df_sim_chief_keyword = pd.read_csv("df_sim_chief_keyword.csv")
    df_sim_chief_keyword.set_index(df_sim_chief_keyword.columns, inplace=True)
    model = pickle.load(open("svd_prediction.pickle", "rb"))

    title_to_id = df_movies.reset_index()[['movieId', 'title']].set_index('title')
    this_movie_id = title_to_id.loc[title]
    all_movieids = list(df_movies.index)
    sim_scores_series = pd.Series(0, index=all_movieids)
    for movieid in all_movieids:
        sim_scores_series.loc[movieid] = \
        df_sim_chief_keyword.loc[df_movies.loc[this_movie_id, 'chief_keyword'], df_movies.loc[movieid, 'chief_keyword']].iloc[0]

    top_25_ids = sim_scores_series.sort_values(ascending=False)[:26].index
    df_movies_top25 = df_movies.loc[top_25_ids].reset_index()

    df_movies_top25['est'] = df_movies_top25['index'].apply(lambda x: model.predict(userId, x).est)

    # Sort the movies in decreasing order of predicted rating
    df_movies_top25 = df_movies_top25.sort_values('est', ascending=False)

    # Return the top 10 movies as recommendations
    resp = Response(response=df_movies_top25.head(10).to_json(orient='records'),
                    status=200,
                    mimetype='application/json')
    return resp

@app.route("/api/hybrid_type/<userId>/<title>", methods=["GET"])
def hybrid_with_movie_type(userId, title):
    types = None
    if request.args['types'].strip():
        types = request.args["types"]
        types = types.split(",")

    df_movies = pd.read_csv("df_movies_final.csv")
    df_movies.set_index("movieId", inplace=True)

    df_sim_chief_keyword = pd.read_csv("df_sim_chief_keyword.csv")
    df_sim_chief_keyword.set_index(df_sim_chief_keyword.columns, inplace=True)
    model = pickle.load(open("svd_prediction.pickle", "rb"))

    top_all = get_movie_recommendation(df_movies, df_movies,userId, title, df_sim_chief_keyword, model)
    # now, going for different type
    data = {}
    data['top_all'] = top_all

    if types:
        for type in types:
            mark = df_movies['genres'].apply(lambda x: type in x)
            df_type_movie = df_movies[mark]
            recommendations = get_movie_recommendation(df_movies, df_type_movie, userId, title, df_sim_chief_keyword, model)
            data[type] = recommendations

    result = jsonify(data)
    result.status_code = 200

    return result

@app.route("/api/test", methods=['GET'])
def test():
    l = {}
    l['a'] = 5
    l['b'] = 10
    result = jsonify(l)
    # result["b"] = 10
    return result


def get_movie_recommendation(df_movies, df_movie_type, userId, title, df_sim_chief_keyword, model):
    title_to_id = df_movies.reset_index()[['movieId', 'title']].set_index('title')
    this_movie_id = title_to_id.loc[title]
    all_movieids = list(df_movie_type.index)
    sim_scores_series = pd.Series(0, index=all_movieids)
    for movieid in all_movieids:
        sim_scores_series.loc[movieid] = \
            df_sim_chief_keyword.loc[
                df_movies.loc[this_movie_id, 'chief_keyword'], df_movie_type.loc[movieid, 'chief_keyword']].iloc[0]

    top_15_ids = sim_scores_series.sort_values(ascending=False)[:16].index
    df_movies_top15 = df_movies.loc[top_15_ids].reset_index()

    df_movies_top15['est'] = df_movies_top15['index'].apply(lambda x: model.predict(userId, x).est)

    # Sort the movies in decreasing order of predicted rating
    df_movies_top15 = df_movies_top15.sort_values('est', ascending=False)
    df_movies_top15['poster'] = df_movies_top15['imdbId'].apply(lambda x: get_image_for_movie(x))
    result = df_movies_top15.to_json(orient='records')
    return result

def get_image_for_movie(imdbId):
    imdbId = str(imdbId)
    while (len(imdbId) < 7):
        imdbId = "0" + imdbId
    imdbId = "tt" + imdbId
    url = "http://www.omdbapi.com/?apikey=b01ac3d3"
    response = requests.get(url, params={'i': imdbId})
    return response.json()["Poster"]


@app.route("/api/collaborative/<userId>", methods=['GET'])
def collaborative(userId):
    types = None
    if request.args['types'].strip():
        types = request.args["types"]
        types = types.split(",")

    df_movies = pd.read_csv("df_movies_final.csv")
    df_movies.set_index("movieId", inplace=True)
    model = pickle.load(open("svd_prediction.pickle", "rb"))

    df_movies['est'] = df_movies.reset_index()['movieId'].apply(lambda x: model.predict(userId, x).est)
    top_all = df_movies.sort_values('est', ascending=False).head(15)
    top_all['poster'] = top_all['imdbId'].apply(lambda x: get_image_for_movie(x))
    top_all = top_all.to_json(orient='records')
    data = {}
    data['top_all'] = top_all

    if types:
        for type in types:
            mark = df_movies['genres'].apply(lambda x: type in x)
            df_type_movie = df_movies[mark]
            recommendations = df_type_movie.sort_values('est', ascending=False).head(15)
            recommendations['poster'] = recommendations['imdbId'].apply(lambda x: get_image_for_movie(x))
            recommendations = recommendations.to_json(orient='records')
            data[type] = recommendations

    result = jsonify(data)
    result.status_code = 200

    return result

@app.route("/api/collaborative/<userId>", methods=['GET'])
def collaborative_types(userId):

    df_movies = pd.read_csv("df_movies_final.csv")
    df_movies.set_index("movieId", inplace=True)
    model = pickle.load(open("svd_prediction.pickle", "rb"))
    df_movies['est'] = df_movies.reset_index()['movieId'].apply(lambda x: model.predict(userId,x).est)
    resp = Response(response=df_movies.sort_values('est', ascending=False).head(10).to_json(orient='records'),
                    status=200,
                    mimetype='application/json')
    return resp

@app.route("/api/movies", methods=['GET'])
def get_all_movie():
    df_movies = pd.read_csv("df_movies_final.csv", usecols=['title','imdbId'])
    resp = Response(response=df_movies.to_json(orient='records'),
                    status=200,
                    mimetype='application/json')
    return resp


def download_data():
    credentail = "IE-Project-ML.json"  # change your credential here
    data_folder = 'movielen-train-model' # change the folder of the bucket here
    bucket_name = "ie-project-ml.appspot.com"  # change your bucket here
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentail

    bucketFolder = environ.get(data_folder)
    # Instantiates a client
    storage_client = storage.Client()
    # The name for the new bucket
    bucket = storage_client.get_bucket(bucket_name)

    files = bucket.list_blobs(prefix=bucketFolder)
    fileList = [file.name for file in files if '.' in file.name]
    for i in fileList:
        blob = bucket.blob(i)
        blob.download_to_filename(i)



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # download_data()
    download_data()
    app.run(port=8080, debug=True)

