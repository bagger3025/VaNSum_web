#!/bin/bash

cp -r ../../../.config .config
docker build -t summarunner --no-cache .
docker container run -d -it --name summaRunner_container summarunner
docker container start summaRunner_container
rm -r .config