#!/bin/bash


docker build -t summarunner --no-cache .
docker container run -d -it --name summaRunner_container summarunner
docker container start summaRunner_container