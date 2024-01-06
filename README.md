_Projet du cours d'Infrastructures et Systèmes Logiciels (S1 3A ENSAE)_

# YouTrend


## Table of Contents

* [About the Project](#about_the_project)
* [Problematic](#prob)
* [Web Application](#web_app)
  * [Installation](#installation)
  * [Access to our app](#access_to_our_app)
* [Contact](#contact)

<br>

## About the Project
The following project is realized as part of the computer science course given by Antoine Chancel during the last year at ENSAE Paris. The main goal is to deploy an app with Docker. This was very challenging and really cool to realize!

<br>

In this repository, you will find the following elements:
* A duration_model folder that contain the model that has been trained and the data used for the train. This model is then used for inference in the app.
* A Docker-compose.yml which orchestrates the containers.
* Some Docker Images : each of the following folder corresponds to an Image to build (with Python):
    * etl : Scrape data from Youtube with Python
    * web_app : Create a user web-app on local host with Dash



## Problematic

This project aims to help YouTube fans or Youtubers, particularly American ones, using data science. To do this, this project includes a Dash web application that provides :

- Insights of current YouTube trends;
- A survival analysis;
- Generate a thumbnail for  based on a Stable Diffusion model. 

The project is built around 2 containers (available on the docker-compose): the data collection and the web-app.

<br>

<!-- WEB APP -->
## Web Application
Our Dash web app allows users to view information about a selected artist() and receive song recommendations using ML. The app is hosted on the local machine at http://localhost:8000/.

The first tab is an overview of the current YouTube trends. Together with the second tab, they provide statistical information such as the average number of views or likes per top creator, as well as others graphs such as the number of trending videos by category, etc... This format allows for an easy understanding of the selected categories and youtubers.

The third tab is a simple duration model. The project is not focused on using machine learning, so we used a simple duration model described in the "Docs" tab. By estimating survival curves (determined using traditional methods), we predicted the probability of entering the trend. Based on the user's desire for an insight of a recent YouTube video (to be chosen by the user himself!), we provide content.

The fourth tab provides access to [a Stable Diffusion model hosted by HuggingFace](https://huggingface.co/stabilityai/stable-diffusion-2-1). First, the user has to [create an HuggingFace account](https://huggingface.co/join) to benefit from HuggingFace API access (it's free so don't hesitate to make it!). After having generated its API token and entered it in our app, the user can finally generate an image. The idea is that the user should enter a video title, and the image can be used (or inspire him) as a video thumbnail.


### Installation
In order to run the code, you will need to follow the following steps:

1. Clone the repository
```sh
git clone https://github.com/Yedson54/YouTrend.git
```
2. Change your current working directory
```sh
cd YouTrend
```
3. Launch the app
Since we have a multi-container Docker application (as defined in the docker-compose.yml), you can run the full project (scraper and web app) by running the following command:

```sh
docker-compose up
```
Note: This can take a bit of time.

### Access to our app:

* http://localhost:8000



## Contact

* [Jules Brablé](https://github.com/JulesBrable) - jules.brable@ensae.fr
* [Yedidia Agnimo](https://github.com/Yedson54) - yedidia.agnimo@ensae.fr
* [Oumar Dione](https://github.com/Oumar-DIONE) - oumar.dione@ensae.fr
* [Louis Latournerie](https://github.com/louislat) - louis.latournerie@ensae.fr
* [Ayman Limae](https://github.com/Liaym) - ayman.limane@ensae.fr
