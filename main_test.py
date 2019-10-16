import pandas as pd
import requests
from google.cloud import storage
import os
# data = pd.read_csv("df_movies_final_ver2.csv")
# data = data.head(2)
# type = 'Animation'
# data['lala'] = None
# print(data.head())
# k = data['keywords'].apply(lambda x: type in x)
# print(data[k])

# def test():
#     data['poster'] = data['imdbId'].apply(lambda x: get_image_for_movie(x))
#     print(data)
# def get_image_for_movie(imdbId):
#     imdbId = str(imdbId)
#     while (len(imdbId) < 7):
#         imdbId = "0" + imdbId
#     imdbId = "tt"+imdbId
#     url = "http://www.omdbapi.com/?apikey=b01ac3d3"
#     response = requests.get(url,params={'i':imdbId})
#     return response.json()["Poster"]
#
# test()
#
# df = pd.read_csv("df_movies_final_ver2.csv",usecols=['title','imdbId'])
# print(df.head())


# Instantiates a client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "IE-Project-ML.json"
storage_client = storage.Client()
# The name for the new bucket

bucket = storage_client.get_bucket("ie-project-ml.appspot.com")

files = bucket.list_blobs(prefix="movielen-train-model")
fileList = [file.name for file in files if '.' in file.name]
for i in fileList:
    print(i)
    # blob = bucket.blob(i)
    # blob.download_to_filename(i)