# Danesfield App

The Danesfield App is a web application for running the [Danesfield](https://github.com/takinekotfs/danesfield) algorithms and visualizing results.  Danesfield addresses the algorithmic challenges of the IARPA CORE3D program by reconstructing semantically meaningful 3D models of buildings and other man-made structures from satellite imagery.

## Video demo

<img src="https://user-images.githubusercontent.com/3123478/49317901-5b759500-f4c4-11e8-9f65-936b718e5f65.gif" />

## Server

### Requirements

* [Download `miniconda` with Python 3.7](https://repo.anaconda.com/miniconda/)

* [`docker` and `docker-compose`](https://www.docker.com/)

### Setup

1. Update `base` of the `miniconda` environment

```shell
conda upgrade --all
```

2. Create, activate new `danesfield` virtual environment

```shell
chmod +x conda/install.sh && conda/install.sh
```

2. Pulling Danesfield docker image from Docker Hub. This image is being maintained by @takinekotfs

```shell
docker pull systakineko/danesfield:linux-amd64
```

3. Install `girder` and its dependencies

```shell
pip install -e server
```

4. **(Optional)** You can edit the *logon* and *password* of admin in `server/init_girder.py`

```python
11 ADMIN_USER = os.getenv("GIRDER_ADMIN_USER", "admin") # Logon is admin
12 ADMIN_PASS = os.getenv("GIRDER_ADMIN_PASS", "1234") # Password is 1234
```

### Running dependent services/applicatons

Girder requires that [MongoDB](https://www.mongodb.com/) and [RabbitMQ](https://www.rabbitmq.com/) are running. If you've installed `docker-compose`, this can be done easily:

```shell
docker-compose up -d
```

You can stop by using this command

```shell
docker-compose stop
```

## Running the application/services

Run the following commands separately on the machine you wish to host the application on (within the conda environment):

```shell
girder serve --host 0.0.0.0 \
python -m girder_worker -l info --concurrency 4
```

## Configuration

Models used:
1. [UNet Semantic Segmentation](https://github.com/Kitware/Danesfield/tree/master/tools#unet-semantic-segmentation)
2. [Building Segmentation](https://github.com/Kitware/Danesfield/tree/master/tools#columbia-building-segmentation)
3. [Material Classification](https://github.com/Kitware/Danesfield/tree/master/tools#material-classification)
4. [Roof Geon Extraction](https://github.com/Kitware/Danesfield/tree/master/tools#roof-geon-extraction)
5. [Run Metrics](https://github.com/Kitware/Danesfield/tree/master/tools#run-metrics)

Upload all [models](https://data.kitware.com/#collection/5fa1b59350a41e3d192de2d5/folder/5fa1b5e150a41e3d192de52b) to the `models` folder within the `core3d` collection, creating it if it doesn't exist.

## Client Setup

### Steps

1. Install `@vue/cli` on global

```shell
npm install -g @vue/cli
```

2. Create `girder` assetstore

3. Enable `danesfield-server` plugin

4. Copy content from `.env` file and create `.env.local` and update the content properly

5. Update and run the server

```shell
npm install
npm run serve
```

### Production deployment with Girder

```shell
npm run build
cp client/dist ./girder/clients/web/static/core3d
```
