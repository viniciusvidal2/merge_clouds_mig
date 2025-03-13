# Merge clouds - MIG
This is the repo to hold the application that treats point clouds coming from more than one source - Drone (SfM) or Sonar. They are properly merged together for the user. It runs as a web application. Follow the tutorials for building and running the app.

## Sample data
You can get a pair of point clouds as sample data to test the application from [this link](https://drive.google.com/file/d/1rf3dvXqQPAVB8wTIXh5d7YCn7X46Wxer/view?usp=sharing) compressed with the name **sample_clouds**. It contains a point cloud captured from drone after the SfM processing, and another one from sonar, also post-processed, namely **drone.ply** and **sonar.ply**. Insert them in the proper fields following the header instructions.

## Instalation
We encourage to use a [conda environment](https://www.anaconda.com/download) to allocate the proper dependencies for this application. To create it with the name **merge_clouds_mig** run the following command:

```bash
cd /path/to/this/repo
conda env create --file=requirements/environment.yml
```

Use the next commands to activate the environment and run the app:

```bash
cd /path/to/this/repo
conda activate merge_clouds_mig
streamlit run app.py
```

## Docker image
### Building and running
Use the command to build the Docker Container. For that you must have [docker](https://docs.docker.com/engine/install/) installed in your machine.

```bash
cd /path/to/this/repo
docker build -f Dockerfile -t merge_clouds_mig:latest .
```

To run the built image you must use the run command:

```bash
docker run --rm -it -p 8501:8501 --name merge_clouds_mig merge_clouds_mig:latest
```

### Get from Dockerhub and run
You can just pull the image from Dockerhub as well and try out in your machine:

```bash
docker pull viniciusfvidal/merge_clouds_mig:latest
docker tag viniciusfvidal/merge_clouds_mig:latest chat-app:latest
docker run --rm -it -p 8501:8501 --name merge_clouds_mig merge_clouds_mig:latest
```
