# IE_Project_Movie_Recommendation
The serveless movie recommendation on Google Cloud Platform

This repository is a about making the movie recommendation system API service run on Google App Engine. This is a part of the project I;ve done in 12 week program in IE under the theme mental health.

The whole project is intened to develop a mobile application under the theme mental health. We work as a group of 4 and we've done almost everything from business analyst, target customer, customer insight to develop application with the help of Agile and Scrum.

As a core developer in the group, I responded for developing an Android mobile application, the RESTful API Webservice by using ASP.NET Core and an API for movie recommendation
The Web API repository can be found [here](https://github.com/nguyenkien1402/IE_Project_WebAPI)
The Android Application can be found [here](https://github.com/nguyenkien1402/IE_Project_AndroidApp)

## What does the this project contain.

Movie_Recommendation_Notebook.ipynb: This notebook comprise the technique and the algorithm i used to create the movie recommendation model. In order to use this note book, there are following steps need to be done.
  1.  Download the MovieLen Dataset in this [link](https://grouplens.org/datasets/movielens/)
  2.  Go to Google Cloud Console and create new account and new project.
  3.  Go to Storage and create new bucket, and put the datasets download above to that bucket.
  4.  Upload the notebook to google colab
  5.  Change the parameter (which i already put the comment what to change) to your parameters such as: bucket_name, bucket_folder..
  6.  Run the notebook, the model will be automatically store in the your bucket folder
  
  
- Import project to PyCharm.
- Install Google Cloud SDK
- Go to Google Console, search credential and create new credentail, save the file as a *<your-name-credential-.json* file in the project
- Go to menu, choose the App Engine and create new standard environment.
- Go the application, change the the credential to your credential you've created above
- Open terminal, cd to the project and type the following cmd to deploy the app
        -   gcloud app init
        -   gcloud deploy app
        
 More information about Google App Engine can be found [here](https://cloud.google.com/appengine/)
